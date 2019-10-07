import axios from 'axios'
import Vue from 'vue'
import router from './router'
import store from './store'

//基础配置
axios.defaults.timeout=5000//超时时间
axios.defaults.baseURL='http://localhost:5000/api'

//添加请求拦截器
axios.interceptors.request.use(function(config){
    //在发送请求前做什么，这里的config就是要发送的请求信息
    const token=window.localStorage.getItem("masonblog-token")
    if(token){
        config.headers.Authorization=`Bearer ${token}`
    }
    return config
},function(error){
    return Promise.reject(error)
})

//添加响应拦截器
axios.interceptors.response.use(function(response){
    //对响应数据做什么
    return response
},function(error){
    //对响应的错误做什么
    switch(error.response.status){
        case 401:
            store.logoutAction()
            if(router.currentRoute.path!=='/login'){
                Vue.toasted.error('401:认证已失效，请先登录',{icon:'fingerprint'})
                router.replace({
                    path:'/login',
                    query:{redirect:router.currentRoute.path}
                })
            }
            break
        case 403:
            Vue.toasted.error('403: Forbidden', { icon: 'fingerprint' })
            router.back()
            break
        case 404:
            Vue.toasted.error('404: NOT FOUND',{icon:'fingerprint'})
            router.back()
            break
        case 500:  // 根本拿不到 500 错误，因为 CORs 不会过来
            Vue.toasted.error('500: Oops... INTERNAL SERVER ERROR', { icon: 'fingerprint' })
            router.back()
            break
    } 
    return Promise.reject(error)
})
export default axios