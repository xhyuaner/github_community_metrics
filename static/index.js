window.addEventListener('load', function(){

  const host = "http://127.0.0.1:5000"

  var container1 = document.getElementById("main");
  var chart1 = echarts.init(container1);
  var container2 = document.getElementById("bottom");
  var chart2 = echarts.init(container2);

  // 处理按钮响应事件
  const searchButton = document.getElementById('search-button');
    searchButton.addEventListener('click', () => {
      const searchBox = document.getElementById('search-box');
      const searchKeyword = searchBox.value;
      // 发送搜索请求到后端
      fetch(`${host}/queryByName?repoName=${searchKeyword}`)
        .then(response => response.json())
        .then(data => {
          console.log(data);
          var dataArray = [];
          for (let key in data) {
            let value = data[key]
            dataArray.push([value.repo_name, value.community_score]);
          }
          let repo_name = dataArray[0][0]
          // 展示搜索结果
          chart2.setOption({
            title: {
              text: `Monthly Community Degree of ${repo_name}`, left: "center" 
            },
            tooltip: {
              trigger: 'axis'
            },
            legend: {
              data: dataArray[0][0]
            },
            grid: { left: '3%',right: '4%',bottom: '3%',containLabel: true },
            xAxis: {
              type: 'category',
              boundaryGap: false,
              data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            },
            yAxis: {
              type: 'value'
            },
            series: [
              {
                // name: 'Video Ads',
                type: 'line',
                stack: 'Total',
                data: dataArray.map(function(item) { return item[1]; })
              }
            ]
          });
        })
        .catch(error => {
          console.error(error);
          // 处理错误
        });
    });
  
  $.ajax({
    url: `${host}/tops`,
    timeout: 60000,
    dataType: 'json',
    success: function(data) {
      console.log(data);
      var dataArray = [];
      for (let key in data) {
        let value = data[key]
        dataArray.push([value.repo_name, value.community_score]);
      }
      // console.log(dataArray);
      chart1.setOption({
      title: { text: `Top 25 Community Degree of Repositories in 2020`, left: "center" },
      grid: {left:'15%',right:'7%',bottom:'7%',containLabel:true},
      xAxis: {
        type: 'category',
        data: dataArray.map(function(item) { return item[0]; }),
        axisLabel: {
          // interval: 0,
          rotate: 40
        }
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          data: dataArray.map(function(item) { return item[1]; }),
          type: 'bar'
        }
      ]
    });
    }
  });
})




  // var url = `./topsByMonth.json`;
  // $.getJSON(url, (data) => {
  //   chart2.setOption({
  //     title: { text: `Index ${type} for ${name}`, left: "center" },
  //     xAxis: {
  //       type: "category",
  //       data: Object.keys(data).filter(k => k.length === 7)
  //     },
  //     yAxis: { type: "value" },
  //     series: [
  //       {
  //         type: "bar",
  //         data: Object.keys(data).filter(k => k.length === 7).map(k => data[k])
  //       }
  //     ]
  //   });
  // });