<template>
  <div>
    <!-- 收到的喜欢或赞列表 -->
    <div class="card border-0 g-mb-15">
      <!-- Panel Header -->
      <div
        class="card-header d-flex align-items-center justify-content-between g-bg-gray-light-v5 border-0 g-mb-15"
      >
        <h3 class="h6 mb-0">
          <i class="icon-bubbles g-pos-rel g-top-1 g-mr-5"></i> Recived Likes
          <small v-if="likes">(共 {{ likes.length}} 条, {{ likes.length }} 页)</small>
        </h3>
        <div class="dropdown g-mb-10 g-mb-0--md">
          <span
            class="d-block g-color-primary--hover g-cursor-pointer g-mr-minus-5 g-pa-5"
            data-toggle="dropdown"
            aria-haspopup="true"
            aria-expanded="false"
          >
            <i class="icon-options-vertical g-pos-rel g-top-1"></i>
          </span>
          <div class="dropdown-menu dropdown-menu-right rounded-0 g-mt-10">
            <router-link
              v-bind:to="{ path: $route.path, query: { page: 1, per_page: 1 }}"
              class="dropdown-item g-px-10"
            >
              <i class="icon-plus g-font-size-12 g-color-gray-dark-v5 g-mr-5"></i> 每页 1 条
            </router-link>
            <router-link
              v-bind:to="{ path: $route.path, query: { page: 1, per_page: 5 }}"
              class="dropdown-item g-px-10"
            >
              <i class="icon-layers g-font-size-12 g-color-gray-dark-v5 g-mr-5"></i> 每页 5 条
            </router-link>
            <router-link
              v-bind:to="{ path: $route.path, query: { page: 1, per_page: 10 }}"
              class="dropdown-item g-px-10"
            >
              <i class="icon-wallet g-font-size-12 g-color-gray-dark-v5 g-mr-5"></i> 每页 10 条
            </router-link>

            <div class="dropdown-divider"></div>

            <router-link
              v-bind:to="{ path: $route.path, query: { page: 1, per_page: 20 }}"
              class="dropdown-item g-px-10"
            >
              <i class="icon-fire g-font-size-12 g-color-gray-dark-v5 g-mr-5"></i> 每页 20 条
            </router-link>
          </div>
        </div>
      </div>
      <!-- End Panel Header -->

      <!-- Panel Body -->
      <div v-if="likes" class="card-block g-pa-0">
        <div
          class="media g-brd-around g-brd-gray-light-v4 g-pa-30 g-mb-20"
          v-for="(like, index) in likes.data"
          v-bind:key="index"
        >
          <router-link v-bind:to="{ path: `/user/${like.from_user}` }">
            <span v-if="like.is_new" class="d-inline-block g-pos-rel">
              <span class="u-badge-v2--xs u-badge--top-left g-bg-red g-mt-7 g-ml-7"></span>
              <img
                class="d-flex g-width-50 g-height-50 rounded-circle g-mt-3 g-mr-15"
                v-bind:src="like.user_avater_link"
                v-bind:alt="like.username"
              />
            </span>
            <img
              v-else
              class="d-flex g-width-50 g-height-50 rounded-circle g-mt-3 g-mr-15"
              v-bind:src="like.user_avater_link"
              v-bind:alt="like.username"
            />
          </router-link>
          <div class="media-body">
            <div class="g-mb-15" v-if="like.flag=='comment_like'">
              <h5 class="h5 g-color-gray-dark-v1 mb-0">
                <router-link
                  v-bind:to="{ path: `/user/${like.from_user}` }"
                  class="comment-author g-text-underline--none--hover"
                >{{ like.user_name }}</router-link>
                <span class="h6">
                  点赞了你的评论
                  <!-- <router-link
                    v-bind:to="{ path: `/post/${like.comment.post.id}#c${like.comment.id}` }"
                    class="g-text-underline--none--hover"
                  >评论</router-link> -->
                </span>
              </h5>
              <span
                class="g-color-gray-dark-v4 g-font-size-12"
              >{{ $moment(like.timestamp).format('YYYY年MM月DD日 HH:mm:ss') }}</span>
            </div>
            <div v-else clas="g-mb-15">
              <!-- 如果是收到文章的点赞 -->
              <h5 class="h5 g-color-gray-dark-v1 mb-0">
                <router-link
                  v-bind:to="{ path: `/user/${like.from_user}` }"
                  class="comment-author g-text-underline--none--hover"
                >{{ like.user_name }}</router-link>
                <span class="h6">
                  点赞了你的文章
                  <router-link
                    v-bind:to="{ path: `/post/${like.post_id}` }"
                    class="g-text-underline--none--hover"
                  >{{like.body}}</router-link>
                </span>
              </h5>
              <span
                class="g-color-gray-dark-v4 g-font-size-12"
              >{{ $moment(like.timestamp).format('YYYY年MM月DD日 HH:mm:ss') }}</span>
            </div>
            <div v-if="like.flag=='comment_like'">
              <!-- vue-markdown 开始解析markdown，它是子组件，通过 props 给它传值即可
              v-highlight 是自定义指令，用 highlight.js 语法高亮 -->
              <vue-markdown
                :source="like.body"
                class="markdown-body g-mb-15"
                v-highlight>
              </vue-markdown>
            </div>
          </div>
        </div>
      </div>
      <!-- End Panel Body -->
    </div>

    <!-- Pagination #04 -->
    <!-- <div v-if="likes && likes._meta.total_pages > 1">
      <pagination
        v-bind:cur-page="likes._meta.page"
        v-bind:per-page="likes._meta.per_page"
        v-bind:total-pages="likes._meta.total_pages"
      ></pagination>
    </div> -->
    <!-- End Pagination #04 -->
  </div>
</template>
<script>
import store from "./../../store"
import VueMarkdown from 'vue-markdown'
import Pagination from '../Base/Pagination'
// bootstrap-markdown 编辑器依赖的 JS 文件，初始化编辑器在组件的 created() 方法中，同时它需要 JQuery 支持哦
import '../../assets/bootstrap-markdown/js/bootstrap-markdown.js'
import '../../assets/bootstrap-markdown/js/bootstrap-markdown.zh.js'
import '../../assets/bootstrap-markdown/js/marked.js'
export default {
  name:'LikeMe',
  data(){
    return{
      shareState:store.state,
      likes:""
    }
  },
  components:{
    VueMarkdown,
    Pagination
  },
  methods:{
    get_notifications(id){
      const path=`/users/${id}/likes/`
      this.$axios.get(path)
      .then((response)=>{
          this.likes=response.data
          console.log(this.likes)
      })
      .catch((error)=>{
          console.error(error);
      })
    }
  },
  created(){
    this.get_notifications(this.shareState.user_id)
  }
}
</script>