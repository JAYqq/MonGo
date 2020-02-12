<template>
  <div class="container g-pt-20">
    <div class="row">
      <!-- Profile Settings -->
      <div class="col-lg-3 g-mb-50">
        <aside class="g-brd-around g-brd-gray-light-v4 rounded g-px-20 g-py-30">
          <!-- Profile Picture -->
          <div v-if="user" class="text-center g-pos-rel g-mb-30">
            <div class="g-width-100 g-height-100 mx-auto mb-3">
              <img class="img-fluid rounded-circle g-brd-around g-brd-gray-light-v4 g-pa-2" v-bind:src="user._links.avatar" v-bind:alt="user.name || user.username">
            </div>

            <span class="d-block g-font-weight-500">{{ user.name || user.username }}</span>

            <router-link v-bind:to="{ path: `/user/${sharedState.user_id}` }">
              <span class="u-icon-v3 u-icon-size--xs g-color-white--hover g-bg-primary--hover rounded-circle g-pos-abs g-top-0 g-right-15 g-cursor-pointer" title="Go To Your Profile"
                    data-toggle="tooltip"
                    data-placement="top">
                <i class="icon-finance-067 u-line-icon-pro"></i>
              </span>
            </router-link>
          </div>
          <!-- End Profile Picture -->

          <hr class="g-brd-gray-light-v4 g-my-30">

          <!-- 左边侧边栏 -->
          <ul class="list-unstyled mb-0">
            <li class="g-pb-3">
              <router-link v-bind:to="{ name: 'RecivedComments' }" v-bind:active-class="'active g-color-primary--active g-bg-gray-light-v5--active'" class="d-block align-middle u-link-v5 g-color-text g-color-primary--hover g-bg-gray-light-v5--hover rounded g-pa-3">
                <span class="u-icon-v1 g-color-gray-dark-v5 mr-2"><i class="icon-finance-205 u-line-icon-pro"></i></span>
                Comments
                <span v-if="notifications.unread_recived_comments_count" class="u-label g-font-size-11 g-bg-pink g-rounded-20 g-px-8 g-ml-15">{{ notifications.unread_recived_comments_count }}</span>
              </router-link>
            </li>
            <li class="g-py-3">
              <router-link v-bind:to="{ name: 'MessagesIndex' }" v-bind:active-class="'active g-color-primary--active g-bg-gray-light-v5--active'" class="d-block align-middle u-link-v5 g-color-text g-color-primary--hover g-bg-gray-light-v5--hover rounded g-pa-3">
                <span class="u-icon-v1 g-color-gray-dark-v5 mr-2"><i class="icon-communication-154 u-line-icon-pro"></i></span>
                Messages
                <span v-if="notifications.unread_messages_count" class="u-label g-font-size-11 g-bg-pink g-rounded-20 g-px-8 g-ml-15">{{ notifications.unread_messages_count }}</span>
              </router-link>
            </li>
            <li class="g-py-3">
              <router-link v-bind:to="{ name: 'FollowMe' }" v-bind:active-class="'active g-color-primary--active g-bg-gray-light-v5--active'" class="d-block align-middle u-link-v5 g-color-text g-color-primary--hover g-bg-gray-light-v5--hover rounded g-pa-3">
                <span class="u-icon-v1 g-color-gray-dark-v5 mr-2"><i class="icon-finance-067 u-line-icon-pro"></i></span>
                Follows
              </router-link>
            </li>
            <li class="g-py-3">
              <router-link v-bind:to="{ name: 'LikeMe'}" v-bind:active-class="'active g-color-primary--active g-bg-gray-light-v5--active'" class="d-block align-middle u-link-v5 g-color-text g-color-primary--hover g-bg-gray-light-v5--hover rounded g-pa-3">
                <span class="u-icon-v1 g-color-gray-dark-v5 mr-2"><i class="icon-medical-022 u-line-icon-pro"></i></span>
                Likes
                <span v-if="notifications.likes_count" class="u-label g-font-size-11 g-bg-pink g-rounded-20 g-px-8 g-ml-15">{{ notifications.likes_count }}</span>
              </router-link>
            </li>

          </ul>
          <!-- End Profile Settings List -->
        </aside>
      </div>
      <!-- End Profile Settings -->

      <!-- Payment Options -->
      <div class="col-lg-9 g-mb-50">
        <!-- Products Block -->
        <div class="rounded g-brd-around g-brd-gray-light-v4 g-overflow-x-scroll g-overflow-x-visible--lg g-pa-30">
          
          <router-view></router-view>

        </div>
        <!-- End Products Block -->
      </div>
      <!-- End Payment Options -->
    </div>
  </div>
</template>

<script>
import store from '../../store'

export default {
  name: 'Notifications',  //this is the name of the component
  data () {
    return {
      sharedState: store.state,
      user: '',
      notification_comment:"",
      notifications:{
         unread_recived_comments_count:0,
         likes_count:0,
         unread_messages_count:0
      }
    }
  },
  methods: {
    getUser (id) {
      const path = `/users/${id}`
      this.$axios.get(path)
        .then((response) => {
          // handle success
          this.user = response.data
        })
        .catch((error) => {
          // handle error
          console.error(error);
        })
    },
    get_notifications(id){
        let since = 0
        const path=`/users/${id}/notifications/?since=${since}`
        this.$axios.get(path)
        .then((response)=>{
            const notifications=response.data
            console.log(response.data)
            for(var i=0;i<notifications.length;i++){
              switch (notifications[i].name) {
                case "unread_recived_comments_count":
                  console.log("unread")
                  this.notifications.unread_recived_comments_count=notifications[i].payload
                  console.log("unread_rececomm"+this.notifications.unread_recived_comments_count)
                  break
                case "liked_commentOrpost_count":
                  this.notifications.likes_count=notifications[i].payload
                  console.log(notifications[i].payload)
                  break
                case "unread_messages_count":
                  console.log("unread_messages_count:  "+response.data[i].payload)
                  this.notifications.unread_messages_count=notifications[i].payload
                  break
                default:
                  break
              }
              since = response.data[i].timestamp
            }
        })
        .catch((error)=>{
            console.error(error);
        })
    }
  },
  created () {
    const user_id = this.sharedState.user_id
    this.getUser(user_id)
    this.get_notifications(user_id)
    $(document).ready(function(){
      $('[data-toggle="tooltip"]').tooltip(); 
    })
  },
  beforeRouteUpdate(to,from,next){
    next()
    this.get_notifications(this.sharedState.user_id)
  }
}
</script>