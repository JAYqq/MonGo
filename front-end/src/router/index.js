import Vue from 'vue'
import Router from 'vue-router'
import Ping from '@/components/Ping'
//首页
import Home from '@/components/Home'
//用户注册登录验证
import Login from '@/components/User/Auth/Login'
import Register from '@/components/User/Auth/Register'
//用户个人设置
import EditProfile from '@/components/User/Settings/EditProfile'
// import Post from '@/components/Base/Post'
//博客详情
import PostDetail from '@/components/PostDetail'
//用户界面
import User from '@/components/User/Settings/User'
//关注界面
import Followers from '@/components/User/Settings/Followers'
import Following from '@/components/User/Settings/Following'

//用户主页
import Overview from '@/components/User/Settings/Overview'
import Settings from '@/components/User/settings/settings'

//用户文章列表
import UserPostsList from '@/components/Post/UserPostsList'
import UserFollowedsPostsList from '@/components/Post/UserFollowedsPostsList'

//设置
import Account from '@/components/User/Settings/Account'
import Email from '@/components/User/Settings/Email'
import Notification from '@/components/User/Settings/Notification'

//用户通知

import Notifications from '@/components/Notification/Notifications'
import RecivedComments from '@/components/Notification/RecivedComments'
Vue.use(Router)

//export 就是一个相当于导出一个模块，这边export那边import
const router = new Router({
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home
    },
    {
      // 博客文章详情页
      path: '/post/:id',
      name: 'PostDetail',
      component: PostDetail
    },
    {
      path: '/login',
      name: 'Login',
      component: Login
    },
    {
      path: '/register',
      name: 'Register',
      component: Register
    },
    {
      path: '/user/:id',
      // name: 'User',
      component: User,
      children: [
        // Overview will be rendered inside User's <router-view>
        // when /user/:id is matched
        // 注意： 要有默认子路由，父路由不能指定 name
        { path: '', component: Overview },
        { path: 'overview', name: 'UserOverview', component: Overview },
				
        // Followers will be rendered inside User's <router-view>
        // when /user/:id/followers is matched
        { path: 'followers', name: 'UserFollowers', component: Followers },

        // Following will be rendered inside User's <router-view>
        // when /user/:id/following is matched
        { path: 'following', name: 'UserFollowing', component: Following },

        // UserPostsList will be rendered inside User's <router-view>
        // when /user/:id/posts is matched
        { path: 'posts', name: 'UserPostsList', component: UserPostsList },

        // UserFollowedsPostsList will be rendered inside User's <router-view>
        // when /user/:id/followeds-posts is matched
        { path: 'followeds-posts', name: 'UserFollowedsPostsList', component: UserFollowedsPostsList }
      ],
      meta: {
        requiresAuth: true
      }
    },
    {
      // 用户修改自己的个人信息
      path: '/settings',
      component: Settings,
      children: [
        { path: '', component: EditProfile },
        { path: 'profile', name: 'SettingProfile', component: EditProfile },
        { path: 'account', name: 'SettingAccount', component: Account },
        { path: 'email', name: 'SettingEmail', component: Email },
        { path: 'notification', name: 'SettingNotification', component: Notification }
      ],
      meta: {
        requiresAuth: true
      }
    },
    {
      path:'/notifications',
      component:Notifications,
      children:[
        {path:'',component:Notification},
        {path:'comments',name:"RecivedComments",component:RecivedComments}
      ],
      meta:{
        requiresAuth:true
      }
    },
    {
      path: '/ping',
      name: 'Ping',
      component: Ping
    }
  ]
})
//导航守卫
/*
功能：
1.检测每次登录路由是否有token
*/
router.beforeEach((to,form,next) => {
  const token=window.localStorage.getItem('masonblog-token')
  if(to.matched.some(record => record.meta.requiresAuth) && (!token || token === null)){
    Vue.toasted.show('Please log in to access this page.', { icon: 'fingerprint' })
    next({
      path:'/login',
      query:{redirect:to.fullPath}//添加重定向参数
    })
  }else if(token&&to.name=='Login'){
    next({
      path:from.fullPath
    })
  }else if(to.matched.length===0){
    Vue.toasted.error('404: NOT FOUND', { icon: 'fingerprint' })
    if(from.name){
      next({
        name:from.name
      })
    }else{
      next({
        path:'/'
      })
    }
  }else{
    next()
  }
})

export default router