/**
 * Created by cody on 6/20/17.
 */
(function docReady() {
  /**
   * Reverse engineered Incapsula's test functions to read, parse, and modify values returned from the test.
   *
   * This allows us to customize the configuration of the program on a per-client basis.
   */
  document.getElementById('run-test').addEventListener('click', function (e) {
    e.preventDefault();
    var o = [["navigator", "exists"], ["navigator.vendor", "value"], ["navigator.appName", "value"], ["navigator.plugins.length==0", "value"], ["navigator.platform", "value"], ["navigator.webdriver", "value"], ["platform", "plugin_extentions"], ["ActiveXObject", "exists"], ["webkitURL", "exists"], ["_phantom", "exists"], ["callPhantom", "exists"], ["chrome", "exists"], ["yandex", "exists"], ["opera", "exists"], ["opr", "exists"], ["safari", "exists"], ["awesomium", "exists"], ["puffinDevice", "exists"], ["__nightmare", "exists"], ["_Selenium_IDE_Recorder", "exists"], ["document.__webdriver_script_fn", "exists"], ["document.$cdc_asdjflasutopfhvcZLmcfl_", "exists"], ["process.version", "exists"], ["navigator.cpuClass", "exists"], ["navigator.oscpu", "exists"], ["navigator.connection", "exists"], ["window.outerWidth==0", "value"], ["window.outerHeight==0", "value"], ["window.WebGLRenderingContext", "exists"], ["document.documentMode", "value"], ["eval.toString().length", "value"]];

    test(o)
  });

  function formatString(v){
    v = v.join();
    v = v.split(",").join("'),<br /> ('");
    v = v.split("%24").join("$");
    v = v.split("%3D%3D").join("==");
    v = v.split("%3D").join("', '");
    v = v.split("%20").join(" ");
    v = "[<br />('" + v + "')<br />]";
    return v;
  }
  function test(o) {
    /**
     * These are the tests that are run on the client browser by Incapsula.
     *
     * To generate this result a website that uses Incapsula was curled and this
     * function was part of the result.  We will use this to tests our users browsers
     * and display the results.
     * @type {string}
     */
    var res = "";
    var vArray = new Array();
    for (var j = 0; j < o.length; j++) {
      var test = o[j][0];
      switch (o[j][1]) {
        case"exists":
          try {
            if (typeof(eval(test)) != "undefined") {
              vArray[vArray.length] = encodeURIComponent(test + "=true")
            } else {
              vArray[vArray.length] = encodeURIComponent(test + "=false")
            }
          } catch (e) {
            vArray[vArray.length] = encodeURIComponent(test + "=false")
          }
          break;
        case"value":
          try {
            try {
              res = eval(test);
              if (typeof(res) === "undefined") {
                vArray[vArray.length] = encodeURIComponent(test + "=undefined")
              } else if (res === null) {
                vArray[vArray.length] = encodeURIComponent(test + "=null")
              } else {
                vArray[vArray.length] = encodeURIComponent(test + "=" + res.toString())
              }
            } catch (e) {
              vArray[vArray.length] = encodeURIComponent(test + "=cannot evaluate");
              break
            }
            break
          } catch (e) {
            vArray[vArray.length] = encodeURIComponent(test + "=" + e)
          }
        case"plugin_extentions":
          try {
            var extentions = [];
            try {
              i = extentions.indexOf("i")
            } catch (e) {
              vArray[vArray.length] = encodeURIComponent("plugin_ext=indexOf is not a function");
              break
            }
            try {
              var num = navigator.plugins.length;
              if (num == 0 || num == null) {
                vArray[vArray.length] = encodeURIComponent("plugin_ext=no plugins");
                break
              }
            } catch (e) {
              vArray[vArray.length] = encodeURIComponent("plugin_ext=cannot evaluate");
              break
            }
            for (var i = 0; i < navigator.plugins.length; i++) {
              if (typeof(navigator.plugins[i]) == "undefined") {
                vArray[vArray.length] = encodeURIComponent("plugin_ext=plugins[i] is undefined");
                break
              }
              var filename = navigator.plugins[i].filename;
              var ext = "no extention";
              if (typeof(filename) == "undefined") {
                ext = "filename is undefined"
              } else if (filename.split(".").length > 1) {
                ext = filename.split('.').pop()
              }
              if (extentions.indexOf(ext) < 0) {
                extentions.push(ext)
              }
            }
            for (i = 0; i < extentions.length; i++) {
              vArray[vArray.length] = encodeURIComponent("plugin_ext=" + extentions[i])
            }
          } catch (e) {
            vArray[vArray.length] = encodeURIComponent("plugin_ext=" + e)
          }
          break
      }
    }
    vArray = formatString(vArray);
    document.getElementById('results').innerHTML = vArray;
  }
})();
