// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import axios from './http'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap/dist/js/bootstrap.js'
import 'bootstrap'
import VueToasted from 'vue-toasted'
import moment from 'moment'

import './assets/core.css'
import './assets/custom.css'

import './assets/icon-line/css/simple-line-icons.css'
import './assets/icon-material/material-icons.css'

// bootstrap-markdown 编辑器需要的样式
import './assets/bootstrap-markdown/css/bootstrap-markdown.min.css'
import './assets/bootstrap-markdown/css/custom.css'
import './assets/icon-awesome/css/font-awesome.min.css'

// markdown 样式
import './assets/markdown-styles/github-markdown.css'
// import hljs from 'highlight.js'
// Vue.use(hljs)
Vue.use(VueToasted,{
  theme:'bubble',
  position:'top-center',
  duration:3000,
  //支持的图标集合
  iconPack:'material',
  action:{
    text:'Cancel',
    onClick:(e,toastObject)=>{
      toastObject.goAway(0)
    }
  },
});
import VueSweetalert2 from 'vue-sweetalert2'
Vue.use(VueSweetalert2)
// 使用 highlight.js 高亮代码。 vue-router 从 Home 页路由到 Post 页后，会重新渲染并且会移除事件
// 注册自定义指令，后续在组件中使用 v-highlight
import hljs from 'highlight.js'
// import 'highlight.js/styles/googlecode.css'
import 'highlight.js/styles/atom-one-dark-reasonable.css'
// 样式文件，浅色：default, atelier-dune-light  深色：atom-one-dark, atom-one-dark-reasonable, monokai
Vue.directive('highlight',function (el) {
  let blocks = el.querySelectorAll('pre code');
  blocks.forEach((block)=>{
    hljs.highlightBlock(block)
  })
})
// hljs.highlightCode =   function () { //自定义highlightCode方法，将只执行一次的逻辑去掉
//   let blocks = document.querySelectorAll('pre code');
//   [].forEach.call(blocks, hljs.highlightBlock);
// };

Vue.config.productionTip = false
//将 $moment 挂载到 prototype 上，在组件中可以直接使用 this.$moment 访问
Vue.prototype.$moment=moment
Vue.prototype.$axios=axios
/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})
