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
import Settings from '@/components/User/Settings/Settings'

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
import Likeme from '@/components/Notification/Likeme'
import FollowMe from'@/components/Notification/FollowMe'
import MessagesHistory from '@/components/Notification/Message/History'
import MessagesIndex from '@/components/Notification/Message/Index'
import RecivedMessages from '@/components/Notification/Message/List'

//用户资源
import Resource from '@/components/Resources/Resource'
import CommentsResource from '@/components/Resources/CommentsResource'
import MessagesIndexResource from '@/components/Resources/Messages/Index'
import SentMessagesResource from '@/components/Resources/Messages/List'
import MessagesHistoryResource from '@/components/Resources/Messages/History'

// 管理后台
import Admin from '@/components/Admin/Admin.vue'
import AdminRoles from '@/components/Admin/Roles.vue'
import AdminUsers from '@/components/Admin/Users.vue'
import AdminPosts from '@/components/Admin/Posts.vue'
import AdminComments from '@/components/Admin/Comments.vue'
import AdminAddRole from '@/components/Admin/AddRole.vue'
import AdminEditRole from '@/components/Admin/EditRole.vue'
import AdminEditUser from '@/components/Admin/EditUser.vue'

//邮件
import Unconfirmed from '@/components/User/Auth/Unconfirmed'
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
      path: '/unconfirmed',
      name: 'Unconfirmed',
      component: Unconfirmed,
      meta: {
        requiresAuth: true
      }
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
      // 用户的资源
      path: '/resource',
      component: Resource,
      children: [
        { path: '', component: UserPostsList },
        { path: 'posts', name: 'PostsResource', component: UserPostsList },
        { path: 'comments', name: 'CommentsResource', component: CommentsResource },
        { 
          path: 'messages', 
          component: MessagesIndexResource,
          children: [
            // 默认匹配，你给哪些人发送过私信
            { path: '', name: "MessagesIndexResource", component: SentMessagesResource },
            // 与某个用户之间的全部历史对话记录
            { path: 'history', name: "MessagesHistoryResource", component: MessagesHistoryResource }
          ]
        }
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
        {path:'comments',name:"RecivedComments",component:RecivedComments},
        { 
          path: 'messages', 
          component: MessagesIndex,
          children: [
            // 默认匹配，哪些人给你发送过私信
            { path: '', name: 'MessagesIndex', component: RecivedMessages },
            // 与某个用户之间的全部历史对话记录
            { path: 'history', name: 'MessagesHistory', component: MessagesHistory }
          ]
        },
        {path:'likeme',name:"LikeMe",component:Likeme},
        {path:'followme',name:"FollowMe",component:FollowMe}
      ],
      meta:{
        requiresAuth:true
      }
    },
    {
      // 管理后台
      path: '/admin',
      component: Admin,
      children: [
        { path: '', component: AdminRoles },
        { path: 'roles', name: 'AdminRoles', component: AdminRoles },
        { path: 'add-role', name: 'AdminAddRole', component: AdminAddRole },
        { path: 'users', name: 'AdminUsers', component: AdminUsers },
        { path: 'posts', name: 'AdminPosts', component: AdminPosts },
        { path: 'comments', name: 'AdminComments', component: AdminComments },
        { path: 'edit-role/:id', name: 'AdminEditRole', component: AdminEditRole },
        { path: 'edit-user/:id', name: 'AdminEditUser', component: AdminEditUser },
      ],
      meta: {
        requiresAuth: true,
        requiresAdmin: true
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
  console.log(to)
  if (token) {
    var payload = JSON.parse(atob(token.split('.')[1]))
    var user_perms = payload.permissions.split(",")
  }
  if(to.matched.some(record => record.meta.requiresAuth) && (!token || token === null)){
    console.log("1")
    //1. 用户未登录，但想访问需要认证的相关路由时，跳转到 登录 页
    Vue.toasted.show('Please log in to access this page.', { icon: 'fingerprint' })
    next({
      path:'/login',
      query:{redirect:to.fullPath}//添加重定向参数
    })
  }else if (token && !payload.confirmed && to.name != 'Unconfirmed') {
    console.log("2")
    // 2. 用户刚注册，但是还没确认邮箱地址时，全部跳转到 认证提示 页面
    Vue.toasted.show('Please confirm your accout to access this page.', { icon: 'fingerprint' })
    next({
      path: '/unconfirmed',
      query: { redirect: to.fullPath }
    })
  } else if (token && payload.confirmed && to.name == 'Unconfirmed') {
    console.log("3")
    // 3. 用户账户已确认，但又去访问 认证提示 页面时不让他过去
    next({
      path: '/'
    })
  }else if(token && (to.name == 'Login' || to.name == 'Register' || to.name == 'ResetPasswordRequest' || to.name == 'ResetPassword')){
    console.log("3")
    //用户已登录，但又去访问 登录/注册/请求重置密码/重置密码 页面时不让他过去
    next({
      path:from.fullPath
    })
  }else if (to.matched.some(record => record.meta.requiresAdmin) && token && !user_perms.includes('admin')) {
    console.log("4")
    // 5. 普通用户想在浏览器地址中直接访问 /admin ，提示他没有权限，并跳转到首页
    Vue.toasted.error('403: Forbidden', { icon: 'fingerprint' })
    next({
      path: '/'
    })
  }else if(to.matched.length===0){
    console.log("5")
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
    console.log("6")
    next()
  }
})

export default router