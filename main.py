"""
    python-openvas
    ================

    This program interact with openvassd (openvas-scanner) to scan an host.
    It features:
    *email report sent to local smtp server
    *json output sent to local flume server
    *IPv4/IPv6 scans
    
    Common use:
    -----------
    Run the default scan and receive the report by email by launching:
    python-openvas -v -i 8.8.8.8 -s john@example.com

    Example:
    --------
    python-openvas -v -i 8.8.8.8 -f General, Malware -s john@example.com
    python-openvas -v -i 8.8.8.8 -j -a

    Advices:
    --------
    Please make sure flume channel capacity are big enough to send a big json 
    in case there are lot of vulnerabilities.

    main module:
    ------------
    This aims at parsing the CLI args, and runing the different functions.
    
"""

import sys, signal, re, socket, argparse #General module
import Email, ParseScan, Ipv4v6, OTP #Personnal class

argv=sys.argv[1:] #put the arguments in a string
parser = argparse.ArgumentParser(description="openvas-handler menu")
parser.add_argument('-a', '--all', help='Scan all the families', action='store_true')
parser.add_argument('-f', '--scan-families', metavar="family1, family2", type=str, nargs='?', dest='family', help="Specify families for the families for the scan.", default= ['Finger abuses', 'Malware', 'Windows : Microsoft Bulletins', 'Netware', 'Default Accounts', 'Buffer overflow', 'Policy', 'Useless services', 'Product detection', 'Denial of Service', 'SSL and TLS', 'Gain a shell remotely', 'Web application abuses', 'Service detection', 'RPC', 'Brute force attacks', 'FTP', 'Compliance', 'Settings', 'Windows', 'Nmap NSE', 'Databases', 'Firewalls', 'Credentials', 'IT-Grundschutz', 'SMTP problems', 'Nmap NSE net', 'CISCO', 'Remote file access', 'SNMP', 'Web Servers', 'General', 'Peer-To-Peer File Sharing', 'Privilege escalation', 'Port scanners', 'IT-Grundschutz-12', 'IT-Grundschutz-13', 'IT-Grundschutz-10', 'IT-Grundschutz-11'])
parser.add_argument('-i', '--ip', metavar='8.8.8.8', type=str ,dest='ip', nargs=1, help="IP of the host to scan")
parser.add_argument('-j', '--json', help="Output the report in JSON and send it to flume",action='store_true')
parser.add_argument('-l', '--list-families', help="List the families available (ex: Windows, Linux, Cisco, etc)", action='store_true')
parser.add_argument('-s', '--email', metavar="x1@example.com, x2@example.com", type=str, nargs="+", help="Send the report to someone@example.com by email", dest="email")
parser.add_argument('-t', '--timeout', type=int, nargs=1, help="Set a timeout for the scan depending if the firewall is up or down. Default is 300s.", dest="timeout",default=300)
parser.add_argument('-v', '--verbose', help="Verbose mode. Output the OTP info in the shell.", dest="verbose",default=False,action='store_true')
args = parser.parse_args()

if args.list_families:
    familyDict = OTP.ListFamilies()
    print(familyDict.keys())
    sys.exit(0)

elif args.ip: #Before Giving the ip to the scanner, test if it is a correct ip.
    isIp = Ipv4v6.Ipv4v6(args.ip[0])
    isIp.valid_ip()

if args.ip and ( args.family or args.all): #Check that we have at least an ip and a family to run the scan
    print("\033[34mDon't forget to deactivate your firewall !\033[0m")
    familyDict = OTP.ListFamilies()
    oidList = OTP.familyToScan(args.all,args.family,familyDict)
    outputScan = OTP.RunScan(args.timeout,args.ip[0],args.verbose,oidList)
    scanReport = ParseScan.ParseScan(outputScan,args.ip[0],familyDict) #Parsing the Scan Section
    if args.json: #user asked for json sent to flume
        scanReport.ParserJSON()
    if args.email: #If the list of destination email has been given, then...
        reportAfterParsing = scanReport.ParserEmail()
	if reportAfterParsing.strip():
            s = Email.Email(reportAfterParsing,args.email)
            s.sendEmail()
	else:
	    print("\033[32mNo Vulnerability detected, then no email sent!\033[0m")
	    sys.exit(0)
else:
    print("\033[31mArguments missing !\033[0m")