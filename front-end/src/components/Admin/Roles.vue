<template>
  <div>
    <router-link v-bind:to="{ name: 'AdminAddRole' }" class="btn btn-outline-success g-mb-15">添加角色</router-link>
    <!-- Striped Rows -->
    <div class="card g-brd-teal rounded-0 g-mb-30">
      <h3
        class="card-header g-bg-teal g-brd-transparent g-color-white g-font-size-16 rounded-0 mb-0"
      >
        <i class="fa fa-edit g-mr-5"></i>
        角色列表
      </h3>

      <div class="table-responsive">
        <table class="table table-striped u-table--v1 mb-0">
          <thead>
            <tr>
              <th>#</th>
              <th>Slug</th>
              <th class="hidden-sm">Name</th>
              <th>Permissions</th>
              <th>Action</th>
            </tr>
          </thead>

          <!-- <tbody>
            <tr v-for="(role, index) in roles.items" v-bind:key="index">
              <th scope="row">{{ index+1 }}</th>
              <td>{{ role.slug }}</td>
              <td class="hidden-sm">{{ role.name }}</td>
              <td>{{ role.permissions }}</td>
              <td>操作</td>
            </tr>
          </tbody> -->

          <tbody>
            <tr v-for="(role, index) in roles.items" v-bind:key="index">
              <th scope="row">{{ index+1 }}</th>
              <td>{{ role.slug }}</td>
              <td class="hidden-sm">{{ role.name }}</td>
              <td>{{ role.permissions }}</td>
              <td>
                <router-link
                  v-bind:to="{ name: 'AdminEditRole', params: { id: role.id } }"
                  class="btn btn-xs u-btn-outline-purple"
                >编辑</router-link>
                <button v-on:click="onDeleteRole(role)" class="btn btn-xs u-btn-outline-red">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <!-- End Striped Rows -->

    <!-- Pagination #04 -->
    <div v-if="roles">
      <pagination
        v-bind:cur-page="roles._meta.page"
        v-bind:per-page="roles._meta.per_page"
        v-bind:total-pages="roles._meta.total_pages"
      ></pagination>
    </div>
    <!-- End Pagination #04 -->
  </div>
</template>

<script>
import Pagination from "../Base/Pagination";
export default {
  name: "Roles", // this is the name of the component
  components: {
    Pagination
  },
  data() {
    return {
      roles: ""
    };
  },
  methods: {
    getRoles() {
      this.roles = "";
      let page = 1;
      let per_page = 10;
      if (typeof this.$route.query.page != "undefined") {
        page = this.$route.query.page;
      }

      if (typeof this.$route.query.per_page != "undefined") {
        per_page = this.$route.query.per_page;
      }

      const path = `/roles/?page=${page}&per_page=${per_page}`;
      this.$axios
        .get(path)
        .then(response => {
          // handle success
          this.roles = response.data;
          console.log(this.roles)
        })
        .catch(error => {
          // handle error
          console.error(error);
        });
    },
    onDeleteRole(role) {
      this.$swal({
        title: "Are you sure?",
        text: "该操作将彻底删除 [ " + role.name + " ], 请慎重",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes, delete it!',
        cancelButtonText: 'No, cancel!'
      }).then((result) => {
        if(result.value) {
          const path = `/roles/${role.id}`
          this.$axios.delete(path)
            .then((response) => {
              // handle success
              this.$swal('Deleted', 'You successfully deleted this role', 'success')
              this.getRoles()
            })
            .catch((error) => {
              // handle error
              console.log(error.response.data)
              this.$toasted.error(error.response.data.message, { icon: 'fingerprint' })
            })
        } else {
          this.$swal('Cancelled', 'The role is safe :)', 'error')
        }
      })
    }
  },
  created() {
    this.getRoles();
  },
  // 当路由变化后(比如变更查询参数 page 和 per_page)重新加载数据
  beforeRouteUpdate(to, from, next) {
    next();
    this.getRoles();
  }
};
</script>