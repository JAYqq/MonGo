<template>
<section>
  <div class="container">
    <nav class="navbar navbar-expand-lg navbar-light bg-light" style="margin-bottom: 20px;">
      <router-link to="/" class="navbar-brand">
        <img src="../../../static/image/icon.png" width="30" height="30" class="d-inline-block align-top" alt="">
          <a href="#" class="g-text-underline--none--hover">Mongo</a>
      </router-link>
      <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <ul class="navbar-nav mr-auto mt-2 mt-lg-0">
          <li class="nav-item active">
            <router-link to="/" class="nav-link">Home <span class="sr-only">(current)</span></router-link>
          </li>
          <li class="nav-item">
            <router-link to="/ping" class="nav-link">Ping</router-link>
          </li>
          <!-- <li class="nav-item" v-if="sharedState.is_authenticated && sharedState.user_perms.includes('admin')">
            <router-link to="/admin" class="nav-link">Admin</router-link>
          </li> -->
        </ul>
        
        <form v-if="sharedState.is_authenticated" class="form-inline navbar-left mr-auto">
          <input class="form-control mr-sm-2" type="search" placeholder="Search">
          <!-- 暂时先禁止提交，后续实现搜索再改回 type="submit" -->
          <button class="btn btn-outline-success my-2 my-sm-0" type="button">Search</button>
        </form>

        <ul v-if="sharedState.is_authenticated" class="nav navbar-nav navbar-right">
          <li class="nav-item g-mr-20">
            <router-link v-bind:to="{ path: '/notifications/comments' }" class="nav-link"><i class="icon-education-033 u-line-icon-pro g-color-red  g-font-size-16 g-pos-rel g-top-2 g-mr-3"></i> Notifications <span id="new_notifications_count" style="visibility: hidden;" class="u-label g-font-size-11 g-bg-aqua g-rounded-20 g-px-10">0</span></router-link>
          </li>
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              <img v-bind:src="sharedState.user_avatar"> {{ sharedState.user_name }}
            </a>
            <div class="dropdown-menu" aria-labelledby="navbarDropdown">
              <router-link v-bind:to="{ path: `/user/${sharedState.user_id}` }" class="dropdown-item">Your profile</router-link>
              <router-link v-bind:to="{ name: 'SettingProfile' }" class="dropdown-item">Settings</router-link>
              <div class="dropdown-divider"></div>
              <a v-on:click="handlerLogout" class="dropdown-item" href="#">Sign out</a>
            </div>
          </li>
        </ul>
        <ul v-else class="nav navbar-nav navbar-right">          
          <li class="nav-item">
            <router-link to="/login" class="nav-link">Sign in</router-link>
          </li>
        </ul>
      </div>
    </nav>
  </div>
</section>
</template>

<script>
import store from '../../store'
import axios from 'axios'
export default {
  name: "Navbar", //name of component
  data(){
    return{
      sharedState:store.state
    }
  },
  methods:{
    handlerLogout(){
      store.logoutAction();
      this.$toasted.show('You have been logged out.',{icon:'fingerprint'})
      this.$router.push('/login')
    }
  },
  //模板渲染完成以后
  mounted(){
    $(function(){
      let since=0
      let total_notifications_count = 0 //总通知
      let unread_recived_comments_count = 0 //没有读过的评论
      let unread_recived_likes_count=0
      if(window.localStorage.getItem('masonblog-token')){
        const payload=JSON.parse(atob(window.localStorage.getItem('masonblog-token').split('.')[1]))
        const user_id=payload.user_id
        console.log("xiixxi")
        setInterval(function(){
          console.log("xiixxi")
          const path=`/users/${user_id}/notifications/?since=${since}`
          axios.get(path)
          .then((response)=>{
            console.log(response.data)
            for(var i=0;i<response.data.length;i++){
              switch(response.data[i].name){
                case "unread_recived_comments_count":
                  console.log("asdasd")
                  unread_recived_comments_count =response.data[i].payload
                  break
                case "liked_commentOrpost_count":
                  unread_recived_likes_count=response.data[i].payload
                  break
              }
              since=response.data[i].timestamp
            }
            // console.log(unread_recived_comments_count)
            total_notifications_count = unread_recived_comments_count+unread_recived_likes_count
            $('#new_notifications_count').text(total_notifications_count)
            $('#new_notifications_count').css('visibility', total_notifications_count ? 'visible' : 'hidden');
          })
          .catch((error)=>{
            console.error(error)
          })
        },10000)
      }
    })
  }
};
</script>

