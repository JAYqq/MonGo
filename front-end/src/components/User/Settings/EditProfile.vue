<template>
  <div class="container">
    <h1>Edit Your Profile</h1>
    <div class="row">
      <div class="col-md-4">
        <form @submit.prevent="onSubmit">
          <div class="form-group">
            <label for="name">Real Name</label>
            <input type="text" v-model="profileForm.name" class="form-control" id="name" placeholder="">
          </div>
          <div class="form-group">
            <label for="location">Location</label>
            <input type="text" v-model="profileForm.location" class="form-control" id="location" placeholder="">
          </div>
          <div class="form-group">
            <label for="about_me">About Me</label>
            <textarea v-model="profileForm.about_me" class="form-control" id="about_me" rows="5" placeholder=""></textarea>
          </div>
          <button type="submit" class="btn btn-primary">Submit</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import store from '../../../store'
export default {
    name:'EditProfile',
    data(){
        return {
            sharedState:store.state,
            profileForm:{
                name:'',
                location:'',
                about_me:'',
                submitted:false
            }
        }
    },
    methods:{
        getUser(id){
            const path=`/users/${id}`
            this.$axios.get(path)
            .then((response)=>{
                this.profileForm.name=response.data.name
                this.profileForm.location=response.data.location
                this.profileForm.about_me=response.data.about_me
            })
            .catch((error)=>{
                console.error(error)
            });
        },
        onSubmit(e){
            const user_id=this.sharedState.user_id
            const path=`/users/${user_id}`
            const payload={
                name:this.profileForm.name,
                location:this.profileForm.location,
                about_me:this.profileForm.about_me
            }
            this.$axios.put(path,payload)
            .then((response)=>{
                this.$toasted.success('Successed modify your profile.',{icon:'fingerprint'})
                this.$router.push({
                    name:'Profile',
                    params:{id:user_id}
                })
            })
            .catch((error)=>{
                console.error(error.response.data)
            })
        }
    },
    created(){
        const user_id=this.sharedState.user_id
        this.getUser(user_id)
    }
}
</script>
