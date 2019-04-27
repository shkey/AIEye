/*

 By shkey

 */

var element;

//用于提示页面
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
    layer.msg('你好，欢迎使用 AIEye 智能白内障检测');
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
        url: '/api/prediction',
        exts: 'jpg|png|jpeg',
        size: 1024,
        before: function (obj) {
            element.progress('cataract', '0%');
            element.progress('normal', '0%');
            $('#p_advice').html('小 AI 暂未给出任何建议哦！');
            //预读本地文件示例，不支持ie8
            obj.preview(function (index, file, result) {
                $('#pre_img').attr('src', result); //图片链接（base64）
            });
        },
        done: function (res) {
            if (res.category == "cataract" || res.category == "normal") {
                element.progress('cataract', res.cataract);
                element.progress('normal', res.normal);
                var per_cataract = parseFloat(res.cataract.replace("%", ""))
                if (per_cataract >= 80) {
                    $('#p_advice').html('小 AI 提醒您，您的眼睛已经极可能患上白内障，请及时联系专业医师进行进一步的诊断！');
                } else if (per_cataract >= 60 && per_cataract < 80) {
                    $('#p_advice').html('小 AI 提醒您，您的眼睛极有可能正在被白内障侵扰，请及时联系专业医师进行进一步的诊断！');
                } else if (per_cataract >= 50 && per_cataract < 60) {
                    $('#p_advice').html('小 AI 稍微有点拿不准，但您的眼睛有很大的可能出现白内障，最好及时联系专业医师进行更精准地诊断！');
                } else if (per_cataract >= 40 && per_cataract < 50) {
                    $('#p_advice').html('小 AI 虽然不太确定，但您的眼睛出现了一些白内障才会有的症状，小 AI 希望您能尽快寻求专业医师的帮助，进行专业的诊断！');
                } else if (per_cataract >= 20 && per_cataract < 40) {
                    $('#p_advice').html('小 AI 温馨提醒，您的眼睛基本没什么问题，出现白内障的可能较小，如果不放心，可向专业医师寻求诊断意见！');
                } else if (per_cataract >= 10 && per_cataract < 20) {
                    $('#p_advice').html('小 AI 基本能打包票，您的眼睛没有和白内障扯上任何关系，如果出了偏差，那一定是机器开了小差！');
                } else if (per_cataract >= 0 && per_cataract < 10) {
                    $('#p_advice').html('小 AI 极其肯定，您的眼睛非常健康，请注意继续保持用眼卫生哦！');
                }
                console.log(res)
            } else {
                element.progress('cataract', '0%');
                element.progress('normal', '0%');
                $('#p_advice').html('请求失败，请重试！');
                obj.preview(function (index, file, result) {
                    $('#pre_img').attr('src', result);
                });
            }
        }
    });
});
