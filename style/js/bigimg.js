jQuery(function(){

//图库关闭层
		 $(".mskeLayBg").height($(document).height());
		 $(".mskeClaose").click(function(){
			 $(".mske_html").html($(".aa").html());
			 $(".mskeLayBg,.mskelayBox").hide();
		 });
		 $(".hidden").hide();
//图库弹出层
		 $(".preview").click(function(){
			 var image_src = $(this).attr("src");
			 $("#example").attr("src",image_src);
			 $(".mske_html").html($(".hidden").html());
			 $(".mskeLayBg").show();
			 $(".mskelayBox").fadeIn(300)
		 });
	 })
	 //屏蔽页面错误
	 jQuery(window).error(function(){
		 return true;
	 });
	 jQuery("img").error(function(){
		 $(this).hide();
	 });

	 function funrotateEvent(obj,arr){
		 var img = document.getElementById(obj);
		 if(!img || !arr) return false;
		 var n = img.getAttribute('step');
		 if(n== null) n=0;
		 if(arr=="left"){
			 (n==0)? n=3:n--;
		 }else if(arr=='right'){
			 (n==3)? n=0:n++;
		 }
		 img.setAttribute('step',n);
		 //对IE浏览器使用滤镜旋转
		 if(document.all) {
			 img.style.filter = 'progid:DXImageTransform.Microsoft.BasicImage(rotation='+ n +')';
			 //HACK FOR MSIE 8
			 switch(n){
				 case 0:
					 img.parentNode.style.height = img.height;
					 break;
				 case 1:
					 img.parentNode.style.height = img.width;
					 break;
				 case 2:
					 img.parentNode.style.height = img.height;
					 break;
				 case 3:
					 img.parentNode.style.height = img.width;
					 break;
			 }
			 // 对现代浏览器写入HTML5的元素进行旋转： canvas
		 }else{
			 var c = document.getElementById('canvas_'+obj);
			 if(c== null){
				 img.style.visibility = 'hidden';
				 img.style.position = 'absolute';
				 c = document.createElement('canvas');
				 c.setAttribute("id",'canvas_'+obj);
				 img.parentNode.appendChild(c);
			 }
			 var canvasContext = c.getContext('2d');
			 switch(n) {
				 default :
				 case 0 :
					 c.setAttribute('width', img.width);
					 c.setAttribute('height', img.height);
					 canvasContext.rotate(0 * Math.PI / 180);
					 canvasContext.drawImage(img, 0, 0, img.width, img.height);
					 break;
				 case 1 :
					 c.setAttribute('width', img.height);
					 c.setAttribute('height', img.width);
					 canvasContext.rotate(90 * Math.PI / 180);
					 canvasContext.drawImage(img, 0, -img.height, img.width, img.height);
					 break;
				 case 2 :
					 c.setAttribute('width', img.width);
					 c.setAttribute('height', img.height);
					 canvasContext.rotate(180 * Math.PI / 180);
					 canvasContext.drawImage(img, -img.width, -img.height, img.width, img.height);
					 break;
				 case 3 :
					 c.setAttribute('width', img.height);
					 c.setAttribute('height', img.width);
					 canvasContext.rotate(270 * Math.PI / 180);
					 canvasContext.drawImage(img, -img.width, 0, img.width, img.height);
					 break;
			 };
		 }
	 }

function selectTag(showContent,selfObj){
	// 操作标签
	var tag = document.getElementById("ul0").getElementsByTagName("li");
	var taglength = tag.length;
	for(i=0; i<taglength; i++){
		tag[i].className = "";
	}
	selfObj.parentNode.className = "selectTag";
	// 操作内容
	for(i=0; j=document.getElementById("tagContent"+i); i++){
		j.style.display = "none";
	}
	document.getElementById(showContent).style.display = "block";	
}

function tagContent0(n)
{
    var a_num=document.getElementById("tagContent0").getElementsByTagName("a");
    var tagval=document.getElementById("tagContent0");
    for(i=0;i<a_num.length;i++)
    {
        if (a_num[i].className=i==n){
	    a_num[i].className = "select";
            console.debug(a_num[i].innerHTML);
            $("#tag0").val(a_num[i].innerHTML);
        }
    }
}

function tagContent1(n)
{
    var a_num=document.getElementById("tagContent1").getElementsByTagName("a");
    for(i=0;i<a_num.length;i++)
    {
        if (a_num[i].className=i==n){
            a_num[i].className = "select";
            console.debug(a_num[i].innerHTML);
            $("#tag1").val(a_num[i].innerHTML);
        }
    }
}

function tagContent2(n)
{
    var a_num=document.getElementById("tagContent2").getElementsByTagName("a");
    for(i=0;i<a_num.length;i++)
    {
        if (a_num[i].className=i==n){
            a_num[i].className = "select";
            console.debug(a_num[i].innerHTML);
            $("#tag2").val(a_num[i].innerHTML);
        }
    }
}

function tagContent3(n)
{
    var a_num=document.getElementById("tagContent3").getElementsByTagName("a");
    for(i=0;i<a_num.length;i++)
    {
        if (a_num[i].className=i==n){
            a_num[i].className = "select";
            console.debug(a_num[i].innerHTML);
            $("#tag3").val(a_num[i].innerHTML);
        }
    }
}

function selectTagx(showContent,selfObj){
	// 操作标签
	var tag = document.getElementById("ul0x").getElementsByTagName("li");
	var taglength = tag.length;
	for(i=0; i<taglength; i++){
		tag[i].className = "";
	}
	selfObj.parentNode.className = "selectTag";
	// 操作内容
	for(i=0; j=document.getElementById("tagContentx"+i); i++){
		j.style.display = "none";
	}
	document.getElementById(showContent).style.display = "block";	
}

function tagContentx0(n)
{
    var a_num=document.getElementById("tagContentx0").getElementsByTagName("a");
    for(i=0;i<a_num.length;i++)
    {
        if (a_num[i].className=i==n){
            a_num[i].className = "select";
            console.debug(a_num[i].innerHTML);
            $("#tag0").val(a_num[i].innerHTML);
        }
    }
}

function tagContentx1(n)
{
    var a_num=document.getElementById("tagContentx1").getElementsByTagName("a");
    for(i=0;i<a_num.length;i++)
    {
        if (a_num[i].className=i==n){
            a_num[i].className = "select";
            console.debug(a_num[i].innerHTML);
            $("#tag1").val(a_num[i].innerHTML);
        }
    }
}

function tagContentx2(n)
{
    var a_num=document.getElementById("tagContentx2").getElementsByTagName("a");
    for(i=0;i<a_num.length;i++)
    {
        if (a_num[i].className=i==n){
            a_num[i].className = "select";
            console.debug(a_num[i].innerHTML);
            $("#tag2").val(a_num[i].innerHTML);
        }
    }
}

function tagContentx3(n)
{
    var a_num=document.getElementById("tagContentx3").getElementsByTagName("a");
    for(i=0;i<a_num.length;i++)
    {
        if (a_num[i].className=i==n){
            a_num[i].className = "select";
            console.debug(a_num[i].innerHTML);
            $("#tag3").val(a_num[i].innerHTML);
        }
    }
}




function selectTagy(showContent,selfObj){
	// 操作标签
	var tag = document.getElementById("ul0y").getElementsByTagName("li");
	var taglength = tag.length;
	for(i=0; i<taglength; i++){
		tag[i].className = "";
	}
	selfObj.parentNode.className = "selectTag";
	// 操作内容
	for(i=0; j=document.getElementById("tagContenty"+i); i++){
		j.style.display = "none";
	}
	document.getElementById(showContent).style.display = "block";	
}

function tagContenty0(n)
{
    var a_num=document.getElementById("tagContenty0").getElementsByTagName("a");
    for(i=0;i<a_num.length;i++)
    {
        if (a_num[i].className=i==n){
            a_num[i].className = "select";
            console.debug(a_num[i].innerHTML);
            $("#tag0").val(a_num[i].innerHTML);
        }
    }
}

function tagContenty1(n)
{
    var a_num=document.getElementById("tagContenty1").getElementsByTagName("a");
    for(i=0;i<a_num.length;i++)
    {
        if (a_num[i].className=i==n){
            a_num[i].className = "select";
            console.debug(a_num[i].innerHTML);
            $("#tag1").val(a_num[i].innerHTML);
        }
    }
}

function tagContenty2(n)
{
    var a_num=document.getElementById("tagContenty2").getElementsByTagName("a");
    for(i=0;i<a_num.length;i++)
    {
        if (a_num[i].className=i==n){
            a_num[i].className = "select";
            console.debug(a_num[i].innerHTML);
            $("#tag2").val(a_num[i].innerHTML);
        }
    }
}

function tagContenty3(n)
{
    var a_num=document.getElementById("tagContenty3").getElementsByTagName("a");
    for(i=0;i<a_num.length;i++)
    {
        if (a_num[i].className=i==n){
            a_num[i].className = "select";
            console.debug(a_num[i].innerHTML);
            $("#tag3").val(a_num[i].innerHTML);
        }
    }
}













