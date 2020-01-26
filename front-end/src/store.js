// 处理一些用户状态切换场景函数
export default {
    debug: true,
    state: {
        is_new: false,
        is_authenticated: window.localStorage.getItem('masonblog-token') ? true : false,
        user_id: window.localStorage.getItem('masonblog-token') ? JSON.parse(window.atob(window.localStorage.getItem("masonblog-token").split('.')[1])).user_id:0,
        user_name: window.localStorage.getItem('masonblog-token') ? JSON.parse(atob(window.localStorage.getItem('masonblog-token').split('.')[1])).user_name : '',
        //多加一次atob，这样重新刷新页面也可以计算出user_avater
        user_avatar:window.localStorage.getItem('masonblog-token')?atob(JSON.parse(atob(window.localStorage.getItem('masonblog-token').split('.')[1])).user_avatar) : '',
        user_perms: window.localStorage.getItem('masonblog-token') ? JSON.parse(atob(window.localStorage.getItem('masonblog-token').split('.')[1])).permissions.split(",") : ''
    },
    setNewAction() {
        if (this.debug) {
            console.log('setNewAction triggered')
            this.state.is_new = true
        }
    },
    resetNotNewAction() {
        if (this.debug) { console.log('resetNotNewAction triggered') }
        this.state.is_new = false
    },
    loginAction() {
        if (this.debug) { console.log('loginAction triggered') }
        this.state.is_authenticated = true
        const payload = JSON.parse(atob(window.localStorage.getItem('masonblog-token').split('.')[1]))
        this.state.user_id=payload.user_id//解析出用户的id
        this.state.user_name = payload.user_name
        this.state.user_avatar = atob(payload.user_avatar)
        this.state.user_perms = payload.permissions.split(",")  // 转换成数组
    },
    logoutAction(){
        if(this.debug){console.log("logoutAction triggered")}
        window.localStorage.removeItem('masonblog-token')
        this.state.is_authenticated=false
        this.state.user_id=0
        this.state.user_name = ''
        this.state.user_avatar = ''
        this.state.user_perms = ''
    }
}