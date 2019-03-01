/*

 By shkey

 */

var element;

//用于演示页面
layui.use(['util'], function () {
    var $ = layui.$,
        util = layui.util;

    //固定Bar
    util.fixbar({
        bar1: true,
        click: function (type) {
            if (type === 'bar1') {
                location.href = 'https://baike.baidu.com/item/%E7%99%BD%E5%86%85%E9%9A%9C';
            }
        }
    });
});

layui.use(['layer', 'form'], function () {
    var layer = layui.layer,
        form = layui.form;
    layer.msg('你好，欢迎使用 AiEye 智能白内障检测');
});

layui.use('element', function () {
    element = layui.element;
});

layui.use('upload', function () {
    var $ = layui.jquery,
        upload = layui.upload;

    //拖拽上传
    upload.render({
        elem: '#upload_area',
        url: '/',
        exts: 'jpg|png|jpeg',
        size: 1024,
        before: function (obj) {
            element.progress('cataract', '0%');
            element.progress('normal', '0%');
            $('#p_advice').html('小 Ai 暂未给出任何建议哦！');
            //预读本地文件示例，不支持ie8
            obj.preview(function (index, file, result) {
                $('#pre_img').attr('src', result); //图片链接（base64）
            });
        },
        done: function (res) {
            element.progress('cataract', res.cataract);
            element.progress('normal', res.normal);
            $('#p_advice').html(res.advice);
            console.log(res)
        }
    });
});
