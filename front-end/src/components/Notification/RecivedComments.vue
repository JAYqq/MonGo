<template>
  <div>
    <!-- Add Comment Form -->
    <form id="replyCommentForm" @submit.prevent="onSubmitReply" @reset.prevent="onResetReply" class="g-mb-40" style="display: none;">
      <div class="form-group">
        <textarea v-model="replyCommentForm.body" class="form-control" id="replyCommentFormBody" rows="5" placeholder=" 评论内容"></textarea>
        <small class="form-control-feedback" v-show="replyCommentForm.bodyError">{{ replyCommentForm.bodyError }}</small>
      </div>
      <button type="reset" class="btn btn-secondary">Cancel</button>
      <button type="submit" class="btn btn-primary">Submit</button>
    </form>
    <!-- End Add Comment Form -->

    <!-- 博客文章的评论列表 -->
    <div class="card border-0 g-mb-15">
      <!-- Panel Header -->
      <div class="card-header d-flex align-items-center justify-content-between g-bg-gray-light-v5 border-0 g-mb-15">
        <h3 class="h6 mb-0">
          <i class="icon-bubbles g-pos-rel g-top-1 g-mr-5"></i> Recived Comments <small v-if="comments">(共 {{ comments._meta.total_items }} 条, {{ comments._meta.total_pages }} 页)</small>
        </h3>
        <div class="dropdown g-mb-10 g-mb-0--md">
          <span class="d-block g-color-primary--hover g-cursor-pointer g-mr-minus-5 g-pa-5" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            <i class="icon-options-vertical g-pos-rel g-top-1"></i>
          </span>
          <div class="dropdown-menu dropdown-menu-right rounded-0 g-mt-10">
            <router-link v-bind:to="{ path: $route.path, query: { page: 1, per_page: 1 }}" class="dropdown-item g-px-10">
              <i class="icon-plus g-font-size-12 g-color-gray-dark-v5 g-mr-5"></i> 每页 1 条
            </router-link>
            <router-link v-bind:to="{ path: $route.path, query: { page: 1, per_page: 5 }}" class="dropdown-item g-px-10">
              <i class="icon-layers g-font-size-12 g-color-gray-dark-v5 g-mr-5"></i> 每页 5 条
            </router-link>
            <router-link v-bind:to="{ path: $route.path, query: { page: 1, per_page: 10 }}" class="dropdown-item g-px-10">
              <i class="icon-wallet g-font-size-12 g-color-gray-dark-v5 g-mr-5"></i> 每页 10 条
            </router-link>
            
            <div class="dropdown-divider"></div>
            
            <router-link v-bind:to="{ path: $route.path, query: { page: 1, per_page: 20 }}" class="dropdown-item g-px-10">
              <i class="icon-fire g-font-size-12 g-color-gray-dark-v5 g-mr-5"></i> 每页 20 条
            </router-link>
            
          </div>
        </div>
      </div>
      <!-- End Panel Header -->
      <!-- Panel Body -->
      <div v-if="comments" class="card-block g-pa-0" >
        
        <div v-bind:id="'c' + comment.id" class="comment-item media g-brd-around g-brd-gray-light-v4 g-pa-30 g-mb-20"
          v-for="(comment, index) in comments.items" v-bind:key="index">
          <router-link v-bind:to="{ path: `/user/${comment.author.id}` }">  
            <span v-if="comment.is_new" class="d-inline-block g-pos-rel">
              <span class="u-badge-v2--xs u-badge--top-left g-bg-red g-mt-7 g-ml-7"></span>
              <img class="d-flex g-width-50 g-height-50 rounded-circle g-mt-3 g-mr-15" v-bind:src="comment.author.avatar" v-bind:alt="comment.author.name || comment.author.username">
            </span>
            <img v-else class="d-flex g-width-50 g-height-50 rounded-circle g-mt-3 g-mr-15" v-bind:src="comment.author.avatar" v-bind:alt="comment.author.name || comment.author.username">
          </router-link>
          <div class="media-body">
            <div class="g-mb-15">
              <h5 class="h5 g-color-gray-dark-v1 mb-0"><router-link v-bind:to="{ path: `/user/${comment.author.id}` }" class="comment-author g-text-underline--none--hover">{{ comment.author.name || comment.author.username }}</router-link> <span class="h6">评论了你的文章<router-link v-bind:to="{ name: 'PostDetail', params: { id: comment.post.id } }" class="g-text-underline--none--hover">《{{ comment.post.title }}》</router-link></span></h5>
              <span class="g-color-gray-dark-v4 g-font-size-12">{{ $moment(comment.timestamp).format('YYYY年MM月DD日 HH:mm:ss') }}</span>
            </div>

            <div v-if="comment.disabled" class="g-color-red g-mb-15">此评论包含不良信息，已被禁止显示.</div>
            <div v-else>
              <!-- vue-markdown 开始解析markdown，它是子组件，通过 props 给它传值即可
              v-highlight 是自定义指令，用 highlight.js 语法高亮 -->
              <vue-markdown
                :source="comment.body"
                class="markdown-body g-mb-15"
                v-highlight>
              </vue-markdown>
            </div>

            <ul class="list-inline d-sm-flex my-0">
              <li v-if="!comment.disabled" class="list-inline-item g-mr-20">
                <a v-on:click="onClickReply(comment)" class="comment-reply-link u-link-v5 g-color-gray-dark-v4 g-color-primary--hover" href="javascript:;">
                  <i class="icon-note g-pos-rel g-top-1 g-mr-3"></i>
                  回复
                </a>
              </li>
              <li class="list-inline-item g-mr-20">
                <router-link v-bind:to="{ path: `/post/${comment.post.id}#c${comment.id}` }" class="u-link-v5 g-color-gray-dark-v4 g-color-primary--hover" href="javascript:;">
                  <i class="icon-action-redo g-pos-rel g-top-1 g-mr-3"></i>
                  查看对话
                </router-link>
              </li>

              <ul class="list-inline mb-0 ml-auto">
                <li v-if="comment.ifread==false" class="list-inline-item ml-auto">
                  <a v-on:click="onMarkRead(comment)" class="u-link-v5 g-color-red g-color-aqua--hover" href="javascript:;">
                    <i class="icon-check g-pos-rel g-top-1 g-mr-3"></i>
                    标为已读
                  </a>
                </li>
                <li v-else class="list-inline-item ml-auto">
                  <span class="u-link-v5 g-color-gray-dark-v4">
                    <i class="icon-check g-pos-rel g-top-1 g-mr-3"></i>
                    已读
                  </span>
                </li>
                <li v-if="!comment.disabled" class="list-inline-item">
                  <button v-on:click="onDisabledComment(comment)" class="btn btn-xs u-btn-outline-purple">屏蔽</button>
                </li>
                <li v-if="comment.disabled" class="list-inline-item">
                  <button v-on:click="onEnabledComment(comment)" class="btn btn-xs u-btn-outline-aqua">恢复</button>
                </li>
                <li class="list-inline-item">
                  <button v-on:click="onDeleteComment(comment)" class="btn btn-xs u-btn-outline-red">删除</button>
                </li>
              </ul>

            </ul>
          </div>
        </div>
      
      </div>
      <!-- End Panel Body -->
    </div>
  
    <!-- Pagination #04 -->
    <div v-if="comments && comments._meta.total_pages > 1">
      <pagination
        v-bind:cur-page="comments._meta.page"
        v-bind:per-page="comments._meta.per_page"
        v-bind:total-pages="comments._meta.total_pages">
      </pagination>
    </div>
    <!-- End Pagination #04 -->
  </div>
</template>
<script>
import store from '../../store'
// 导入 vue-markdown 组件解析 markdown 原文为　HTML
import VueMarkdown from 'vue-markdown'
import Pagination from '../Base/Pagination'
// bootstrap-markdown 编辑器依赖的 JS 文件，初始化编辑器在组件的 created() 方法中，同时它需要 JQuery 支持哦
import '../../assets/bootstrap-markdown/js/bootstrap-markdown.js'
import '../../assets/bootstrap-markdown/js/bootstrap-markdown.zh.js'
import '../../assets/bootstrap-markdown/js/marked.js'
export default {
    name:'RecivedComments',
    data(){
      return{
        sharestate:store.state,
        comments:"",
        replyCommentForm:{
          body: '',
          post_id: '',  // 被回复的评论来自哪篇博客
          parent_id: '',  // 被回复的评论的 id
          author_id: '',  // 被回复的评论的作者的 id
          author_name: '',  // 被回复的评论的作者的名字
          errors: 0,  // 表单是否在前端验证通过，0 表示没有错误，验证通过
          bodyError: null
        }
      }
    },
    components:{
      VueMarkdown,
      Pagination
    },
    methods:{
      getUserRecivedComments(id){
        let page=1
        let per_page=5
        if(typeof this.$route.query.page!='undefined'){
          page=this.$route.query.page
        }
        if(typeof this.$route.query.per_page!='undefined'){
          per_page=this.$route.query.per_page
        }
        const path=`/users/${id}/reveived_comment/?page=${page}&per_page=${per_page}`
        this.$axios.get(path)
        .then((responce)=>{
          console.log(responce.data)
          this.comments=responce.data
        })
        .catch((error)=>{
          console.error(error)
        })
      },
      onMarkRead(comment){
        const path=`/comments/removemark/${comment.id}`
        this.$axios.get(path)
        .then((response)=>{
          console.log(response.data)
          this.getUserRecivedComments(this.sharestate.user_id)
        })
        .catch((error)=>{
          console.error(error)
        })
      }
    },
    created(){
      this.getUserRecivedComments(this.sharestate.user_id)
    },
    beforeRouteUpdate(to,from,next){
      next()
      this.getUserRecivedComments(this.sharestate.user_id)
    }
}
</script>
