<!DOCTYPE html>
<html lang="zh-TW">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Kai-xiu Chen</title>
	<style type="text/css">
		* { font-family:"標楷體"; margin-left:auto; margin-right:auto;}
		h1 {color:blue; font-size:60px;}
		h2 {color:#33ff33; font-size:40px;}
	</style>

	<script>
		function change1() {
  			document.getElementById("pic").src = "static/mountain.jpg";
  			document.getElementById("h2text").innerText = "靜宜資管";
		}

		function change2() {
  			document.getElementById("pic").src = "static/cliff.jpg";
  			document.getElementById("h2text").innerText = "Kai-xiu Chen";
		}
	</script>


</head>
<body>
	
</body>
</html>
    <table width="70%">
		<tr>
			<td>
				<img src="static/cliff.jpg" width="110%"id="pic" onmouseover="change1()" onmouseout="change2()"></img>
			</td>

			<td>


    <h1>陳楷修<h1>
    <h2>Kai-xiu Chen<h2>

    </td>
		</tr>
	</table>

<?php echo date("Y-m-d") ?>

<table width="70%" border="1">
		<tr>
			<td>

    
    個人網頁<br>
    
</body>


    </td>

			<td>


    大象席地而坐電影配樂<br>
	<audio controls>
		<source src="static/elephant.mp3" type="audio/mP3">
	</audio><br>

	</td>

			<td>



    不要去台灣<br>
    <iframe src="https://www.youtube.com/embed/pW88QFpHXa8" allowfullscreen></iframe>


    </td>
		</tr>
	</table>		

	<a href=/>回首頁</a>
	<a href=/mis>課程</a><hr>
	<a href=/today>今日日期</a><hr>

</body>    
</html>