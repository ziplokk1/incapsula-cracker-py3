from __future__ import unicode_literals
import unittest

from incapsula import IncapSession


# ToDo: Test case for when re-captcha is typing the text from the pictures.

# ToDo: Test case for when re-captcha is finding objects in pictures.


class TestIncapBlocked(unittest.TestCase):
    """
    Test case for when the request is blocked by incapsula.
    """
    body = """
    <html style="height:100%"><head><META NAME="ROBOTS" CONTENT="NOINDEX, NOFOLLOW"><meta name="format-detection" content="telephone=no"><meta name="viewport" content="initial-scale=1.0"><meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"><script type="text/javascript" src="/_Incapsula_Resource?SWJIYLWA=2977d8d74f63d7f8fedbea018b7a1d05"></script></head><body style="margin:0px;height:100%"><iframe src="/_Incapsula_Resource?CWUDNSAI=18&xinfo=10-145639306-0 0NNN RT(1495555623413 147) q(0 -1 -1 -1) r(0 -1) B15(11,4636,0) U5&incident_id=220011010269131805-850355021556761818&edet=15&cinfo=0b000000" frameborder=0 width="100%" height="100%" marginheight="0px" marginwidth="0px">Request unsuccessful. Incapsula incident ID: 220011010269131805-850355021556761818</iframe></body></html>
    """

    def test_incap_blocked(self):
        s = IncapSession()
        self.assertTrue(s.incap_blocked(self.body))


class TestIncapBlockedNoCaptchaIframe(unittest.TestCase):
    """
    Iframe contains link to javascript code in //content.incapsula.com/jsTest.html instead of captcha.
    """
    body = """
    <html>
    <head>
    <META NAME="robots" CONTENT="noindex,nofollow">
    <script>
    (function(){function getSessionCookies(){var cookieArray=new Array();var cName=/^\s?incap_ses_/;var c=document.cookie.split(";");for(var i=0;i<c.length;i++){var key=c[i].substr(0,c[i].indexOf("="));var value=c[i].substr(c[i].indexOf("=")+1,c[i].length);if(cName.test(key)){cookieArray[cookieArray.length]=value}}return cookieArray}function setIncapCookie(vArray){var res;try{var cookies=getSessionCookies();var digests=new Array(cookies.length);for(var i=0;i<cookies.length;i++){digests[i]=simpleDigest((vArray)+cookies[i])}res=vArray+",digest="+(digests.join())}catch(e){res=vArray+",digest="+(encodeURIComponent(e.toString()))}createCookie("___utmvc",res,20)}function simpleDigest(mystr){var res=0;for(var i=0;i<mystr.length;i++){res+=mystr.charCodeAt(i)}return res}function createCookie(name,value,seconds){var expires="";if(seconds){var date=new Date();date.setTime(date.getTime()+(seconds*1000));var expires="; expires="+date.toGMTString()}document.cookie=name+"="+value+expires+"; path=/"}function test(o){var res="";var vArray=new Array();for(var j=0;j<o.length;j++){var test=o[j][0];switch(o[j][1]){case"exists":try{if(typeof(eval(test))!="undefined"){vArray[vArray.length]=encodeURIComponent(test+"=true")}else{vArray[vArray.length]=encodeURIComponent(test+"=false")}}catch(e){vArray[vArray.length]=encodeURIComponent(test+"=false")}break;case"value":try{try{res=eval(test);if(typeof(res)==="undefined"){vArray[vArray.length]=encodeURIComponent(test+"=undefined")}else if(res===null){vArray[vArray.length]=encodeURIComponent(test+"=null")}else{vArray[vArray.length]=encodeURIComponent(test+"="+res.toString())}}catch(e){vArray[vArray.length]=encodeURIComponent(test+"=cannot evaluate");break}break}catch(e){vArray[vArray.length]=encodeURIComponent(test+"="+e)}case"plugin_extentions":try{var extentions=[];try{i=extentions.indexOf("i")}catch(e){vArray[vArray.length]=encodeURIComponent("plugin_ext=indexOf is not a function");break}try{var num=navigator.plugins.length;if(num==0||num==null){vArray[vArray.length]=encodeURIComponent("plugin_ext=no plugins");break}}catch(e){vArray[vArray.length]=encodeURIComponent("plugin_ext=cannot evaluate");break}for(var i=0;i<navigator.plugins.length;i++){if(typeof(navigator.plugins[i])=="undefined"){vArray[vArray.length]=encodeURIComponent("plugin_ext=plugins[i] is undefined");break}var filename=navigator.plugins[i].filename;var ext="no extention";if(typeof(filename)=="undefined"){ext="filename is undefined"}else if(filename.split(".").length>1){ext=filename.split('.').pop()}if(extentions.indexOf(ext)<0){extentions.push(ext)}}for(i=0;i<extentions.length;i++){vArray[vArray.length]=encodeURIComponent("plugin_ext="+extentions[i])}}catch(e){vArray[vArray.length]=encodeURIComponent("plugin_ext="+e)}break}}vArray=vArray.join();return vArray}var o=[["navigator","exists"],["navigator.vendor","value"],["navigator.appName","value"],["navigator.plugins.length==0","value"],["navigator.platform","value"],["navigator.webdriver","value"],["platform","plugin_extentions"],["ActiveXObject","exists"],["webkitURL","exists"],["_phantom","exists"],["callPhantom","exists"],["chrome","exists"],["yandex","exists"],["opera","exists"],["opr","exists"],["safari","exists"],["awesomium","exists"],["puffinDevice","exists"],["__nightmare","exists"],["_Selenium_IDE_Recorder","exists"],["document.__webdriver_script_fn","exists"],["document.$cdc_asdjflasutopfhvcZLmcfl_","exists"],["process.version","exists"],["navigator.cpuClass","exists"],["navigator.oscpu","exists"],["navigator.connection","exists"],["window.outerWidth==0","value"],["window.outerHeight==0","value"],["window.WebGLRenderingContext","exists"],["document.documentMode","value"],["eval.toString().length","value"]];try{setIncapCookie(test(o));document.createElement("img").src="/_Incapsula_Resource?SWKMTFSR=1&e="+Math.random()}catch(e){img=document.createElement("img");img.src="/_Incapsula_Resource?SWKMTFSR=1&e="+e}})();
    </script>
    <script>
    (function() { 
    var z="";var b="7472797B766172207868723B76617220743D6E6577204461746528292E67657454696D6528293B766172207374617475733D227374617274223B7661722074696D696E673D6E65772041727261792833293B77696E646F772E6F6E756E6C6F61643D66756E6374696F6E28297B74696D696E675B325D3D22723A222B286E6577204461746528292E67657454696D6528292D74293B646F63756D656E742E637265617465456C656D656E742822696D6722292E7372633D222F5F496E63617073756C615F5265736F757263653F4553324C555243543D363726743D373826643D222B656E636F6465555249436F6D706F6E656E74287374617475732B222028222B74696D696E672E6A6F696E28292B222922297D3B69662877696E646F772E584D4C4874747052657175657374297B7868723D6E657720584D4C48747470526571756573747D656C73657B7868723D6E657720416374697665584F626A65637428224D6963726F736F66742E584D4C4854545022297D7868722E6F6E726561647973746174656368616E67653D66756E6374696F6E28297B737769746368287868722E72656164795374617465297B6361736520303A7374617475733D6E6577204461746528292E67657454696D6528292D742B223A2072657175657374206E6F7420696E697469616C697A656420223B627265616B3B6361736520313A7374617475733D6E6577204461746528292E67657454696D6528292D742B223A2073657276657220636F6E6E656374696F6E2065737461626C6973686564223B627265616B3B6361736520323A7374617475733D6E6577204461746528292E67657454696D6528292D742B223A2072657175657374207265636569766564223B627265616B3B6361736520333A7374617475733D6E6577204461746528292E67657454696D6528292D742B223A2070726F63657373696E672072657175657374223B627265616B3B6361736520343A7374617475733D22636F6D706C657465223B74696D696E675B315D3D22633A222B286E6577204461746528292E67657454696D6528292D74293B6966287868722E7374617475733D3D323030297B706172656E742E6C6F636174696F6E2E72656C6F616428297D627265616B7D7D3B74696D696E675B305D3D22733A222B286E6577204461746528292E67657454696D6528292D74293B7868722E6F70656E2822474554222C222F5F496E63617073756C615F5265736F757263653F535748414E45444C3D383530313837373334383339363338383639392C373530353031363132313139343934323832342C383232353934363931363531373334373334332C373235353131222C66616C7365293B7868722E73656E64286E756C6C297D63617463682863297B7374617475732B3D6E6577204461746528292E67657454696D6528292D742B2220696E6361705F6578633A20222B633B646F63756D656E742E637265617465456C656D656E742822696D6722292E7372633D222F5F496E63617073756C615F5265736F757263653F4553324C555243543D363726743D373826643D222B656E636F6465555249436F6D706F6E656E74287374617475732B222028222B74696D696E672E6A6F696E28292B222922297D3B";for (var i=0;i<b.length;i+=2){z=z+parseInt(b.substring(i, i+2), 16)+",";}z = z.substring(0,z.length-1); eval(eval('String.fromCharCode('+z+')'));})();
    </script></head>
    <body>
    <iframe style="display:none;visibility:hidden;" src="//content.incapsula.com/jsTest.html" id="gaIframe"></iframe>
    </body></html>
    """

    def test_incap_blocked(self):
        s = IncapSession()
        self.assertTrue(s.incap_blocked(self.body))


class TestIncapBlockedCheckboxCaptcha(unittest.TestCase):
    """
    Test case for when incapsula is blocked by a checkbox captcha.
    """
    body = """
    <div class="container">
        <div class="container-inner">
            <div class="main">
                <div class="main-inner">
                    <div class="error-headline">
                        <div class="headline-inner">
                            <h1>dollargeneral.com -</h1>
                            <p>Additional security check is required</p>
                        </div>
                    </div>
                    <div class="error-content">
                        <div class="captcha">
                            <div class="form_container">
                                <div class="g-recaptcha" data-sitekey="6Ld38BkUAAAAAPATwit3FXvga1PI6iVTb6zgXw62" data-callback="onCaptchaFinished" ></div>
                            </div>
                        </div>
                    </div>
                </div>
    
                <div class="powered-by">
                    <span class="text">Powered by</span>
                    <a href="//www.incapsula.com/why-am-i-seeing-this-page.html?src=23&amp;utm_source=blockingpages" target="_blank" class="copyrights">Incapsula</a>
                </div>
    
                <div class="info-text">
                    <strong>What is this page?</strong>
                    <p>The web site you are visiting is protected and accelerated by Incapsula. Your computer might have been infected by some kind of malware and flagged by Incapsula network. This page is presented by Incapsula to verify that a human is behind the traffic to this site and not malicious software.</p>
    
                    <strong>What should i do?</strong>
                    <p>Simply enter the two words in the image above to pass the security check, once you do that we will remember your answer and will not show this page again. You should run a virus and malware scan on your computer to remove any infection.</p>
                </div>
            </div>
        </div>
    </div>
    """
    def test_incap_recaptcha_blocked(self):
        s = IncapSession()
        self.assertTrue(s.html_is_recaptcha(self.body))
