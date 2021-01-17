(function(t){function e(e){for(var r,u,c=e[0],i=e[1],s=e[2],l=0,p=[];l<c.length;l++)u=c[l],Object.prototype.hasOwnProperty.call(o,u)&&o[u]&&p.push(o[u][0]),o[u]=0;for(r in i)Object.prototype.hasOwnProperty.call(i,r)&&(t[r]=i[r]);f&&f(e);while(p.length)p.shift()();return a.push.apply(a,s||[]),n()}function n(){for(var t,e=0;e<a.length;e++){for(var n=a[e],r=!0,c=1;c<n.length;c++){var i=n[c];0!==o[i]&&(r=!1)}r&&(a.splice(e--,1),t=u(u.s=n[0]))}return t}var r={},o={app:0},a=[];function u(e){if(r[e])return r[e].exports;var n=r[e]={i:e,l:!1,exports:{}};return t[e].call(n.exports,n,n.exports,u),n.l=!0,n.exports}u.m=t,u.c=r,u.d=function(t,e,n){u.o(t,e)||Object.defineProperty(t,e,{enumerable:!0,get:n})},u.r=function(t){"undefined"!==typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},u.t=function(t,e){if(1&e&&(t=u(t)),8&e)return t;if(4&e&&"object"===typeof t&&t&&t.__esModule)return t;var n=Object.create(null);if(u.r(n),Object.defineProperty(n,"default",{enumerable:!0,value:t}),2&e&&"string"!=typeof t)for(var r in t)u.d(n,r,function(e){return t[e]}.bind(null,r));return n},u.n=function(t){var e=t&&t.__esModule?function(){return t["default"]}:function(){return t};return u.d(e,"a",e),e},u.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},u.p="/";var c=window["webpackJsonp"]=window["webpackJsonp"]||[],i=c.push.bind(c);c.push=e,c=c.slice();for(var s=0;s<c.length;s++)e(c[s]);var f=i;a.push([0,"chunk-vendors"]),n()})({0:function(t,e,n){t.exports=n("56d7")},"00cf":function(t,e,n){"use strict";n("f7c8")},"56d7":function(t,e,n){"use strict";n.r(e);n("e260"),n("e6cf"),n("cca6"),n("a79d");var r=n("2b0e"),o=function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("LogList")},a=[],u=n("8323"),c=n.n(u),i=n("263c"),s=n.n(i),f=function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("div",{attrs:{id:"main"}},[n("div",{attrs:{"uk-grid":""}},[n("div",{staticClass:"uk-width-expand@m"},[n("pre",[t._v("producing "+t._s(t.formatProduction(t.stats.Queue)))]),t._l(t.stats.Processes,(function(e){return n("pre",{key:e.Pid},[t._v(t._s(e.Name)+" ("+t._s(e.PID)+"): cpu: "+t._s(t.formatPercent(e.CPU))+"% / memory: "+t._s(t.formatPercent(e.Memory))+"%")])})),n("hr"),n("table",{staticClass:"uk-table"},[t._m(0),t._l(t.logs,(function(e){return n("tbody",{key:e.ID},[n("tr",[n("td",[t._v(t._s(t.formatID(e.ID)))]),n("td",[t._v(t._s(t.formatDate(e.ModTime)))]),n("td",[t._v(t._s(t.formatOutput(e.Output)))])])])}))],2)],2)])])},l=[function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("thead",[n("tr",[n("th",{attrs:{width:"120"}},[t._v("ID")]),n("th",[t._v("Time")]),n("th",[t._v("Status")])])])}],p=(n("a15b"),n("a9e3"),n("b680"),n("ac1f"),n("1276"),n("bc3a")),d=n.n(p),v=n("5a0c"),h=n.n(v),m=n("f906"),g=n("4208");n("9e30");h.a.extend(m),h.a.extend(g),h.a.locale("en");var _={name:"LogList",data:function(){return{document:{},logs:[],stats:{}}},mounted:function(){var t=this;setInterval((function(){t.getLogList(),t.getStats()}),1e3)},methods:{getLogList:function(){var t=this;d.a.get("http://0.0.0.0:4000/api/logs").then((function(e){e.data?t.logs=e.data.reverse():t.logs=[]})).catch((function(t){console.log(t)}))},getStats:function(){var t=this;d.a.get("http://0.0.0.0:4000/api/stats").then((function(e){t.stats=e.data})).catch((function(t){console.log(t)}))},formatDate:function(t){var e=h()(t);return e.fromNow()},formatID:function(t){return t.split("/")[2].split(".")[0]},formatOutput:function(t){return t},formatProduction:function(t){return t&&t.length>0?t.join(", "):"nothing"},formatPercent:function(t){return Number(t.toFixed(2))}}},b=_,y=(n("00cf"),n("2877")),P=Object(y["a"])(b,f,l,!1,null,"5a702c46",null),O=P.exports;n("30b0");c.a.use(s.a);var w={name:"PrefectApp",components:{LogList:O}},j=w,x=Object(y["a"])(j,o,a,!1,null,null,null),L=x.exports;r["a"].config.productionTip=!1,new r["a"]({render:function(t){return t(L)}}).$mount("#app")},f7c8:function(t,e,n){}});
//# sourceMappingURL=app.3d7aec55.js.map