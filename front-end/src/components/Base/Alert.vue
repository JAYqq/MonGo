<template>
    <div class="alert" role="alert" v-bind:class="'alert-'+variant">
        {{message}}
    </div>
</template>
<script>
export default {
    props:['variant','message']//可以接收父组件传递的 variant 和 message 数据
}
</script>
