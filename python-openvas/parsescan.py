import time,json,collections, socket, os, progressbar , oid

class ParseScan:

    """
        This class aims at parsing the report of the server to 2 format:
        email readable format and elasticsearch Json format
    """

    def __init__(self,target,familyDict):
        self.target = target
        self.report = ""
        self.familyDict = familyDict #required for  name & description of plugin oid
        self.jsonDict = [] #jsonDict is an array containing the Json Dictionnary
	self.oidObj = oid.Oid(familyDict)

    def _CreateTemplate(self):
        """
            Create Template Dictionnary which respects Flume default template.
        """
	templateDict = {
'headers' : {
	'timestamp' : str(int(time.time())) ,
	'host' : socket.gethostname()
	}
}
	return templateDict

    def _CreateBody(self,motiv):
	"""
	    Create Body Dictionnary inserted in templateDict['body'] as JSON.
	"""
	motivParsed = motiv.split("<|> ")
	oidNumber = motivParsed[4].strip()
	familyOfOid = self.oidObj.SearchFamily(oidNumber)
	bodyDict = {
"target" : self.target ,
"plugin" : {
        "name" : self.familyDict[familyOfOid][oidNumber]["name"],
        "description" : self.familyDict[familyOfOid][oidNumber]["description"],
	"family" : familyOfOid,
        "oid" : oidNumber,
        "CVE" : self.familyDict[familyOfOid][oidNumber]["CVE"],
        "BID" : self.familyDict[familyOfOid][oidNumber]['BID'],
        "URL" : self.familyDict[familyOfOid][oidNumber]["URL"],
        "grade" : self.familyDict[familyOfOid][oidNumber]["grade"],
        "message" : str(motivParsed[3]),
        "type": "LOG" if "LOG <|>" in motiv else "ALARM"
	}
}
	return bodyDict

    def AddLine(self,outputScanLine,verbose):
        """
            ParserJson est le Parser qui renvoie le Json contenant
            les logs du scan.
            Afin de correspondre au JsonHandler de Flume, voici sa forme
        """
	if verbose:
	    def print_verbose(x) : print(x)
	else:
	    def print_verbose(x): None
	print_verbose(outputScanLine)
        scanList = outputScanLine.split("SERVER <|>")
        for motiv in scanList:
	    if "LOG <|>" in motiv or "ALARM <|>" in motiv:
		templateDict = self._CreateTemplate()
		self.jsonDict.append(templateDict.copy())
		bodyDict = self._CreateBody(motiv)
		bodyJson = json.dumps(bodyDict)
                self.jsonDict[len(self.jsonDict)-1]["body"] = bodyJson
	    elif 'STATUS <|>' in motiv and not verbose:
		current_no_of_completed_tests, total_no_of_tests = motiv.split(' <|> ')[2].split('/')
		if int(current_no_of_completed_tests) == 0:
		    self.pbar = progressbar.ProgressBar(maxval = int(total_no_of_tests)).start()
		self.pbar.update(int(current_no_of_completed_tests))
        return 0

    def FinalOutput(self,verbose):
	if not verbose:
	    self.pbar.finish()
	jsonOutput = json.dumps(self.jsonDict)	
	return jsonOutput

