// JavaScript Document
jQuery.postJSON = function(url, data, callback) {
　　jQuery.post(url, data, callback, "json");
};

//ホームの投稿ボタン処理
$(function() { 
  $("#homeListButton").live("click", function(){
    location.href = "#list?&"
                  + this.name;
  });
});

//新規投稿処理
$(function() {
  var flag = 0;
  $("#btn2").click(function() {
    if($("#title").val() !== "" && $("#body").val() !== ""){
      if(flag == 0){
        flag++;
        url = "http://em-home.appspot.com/postComment";
        req = {
          "displayName":"",
          "name":"test",//$("#name").val(),
          "title":$("#title").val(),
          "body":$("#body").val(),
          "category":$("#select").val(),
          "callback":"?"
        };
        $.post(url, req, callback);
      }
    }
    else{
      alert("未入力の項目があります");
    }
  });
  var callback = function(json){
    if(json == "0"){
      alert("投稿に失敗しました¥nやり直してください");
      flag = 0;
    }else{
      document.getElementById("title").value ='';
      document.getElementById("body").value ='';
      flag = 0;
      alert("投稿が完了しました");
      //location.href = "#userhome";
      //location.reload(true);
    }
  };
});
//新規投稿処理おわり

//list処理
var resJson = [];
$(function() { 
  $(document).delegate("#list", "pagebeforeshow", function(){
    var categoryHash = document.location.hash;
    var category = categoryHash.split("&");
  
    $("#listView").html('');
    var icount = 0;
    var lim = 10;
    var off = 0;
    var cat = category[1];
    loadCategoryList(cat,lim,off);
    icount = resJson.length;
    if(icount < 9){
      document.getElementById('moreRead').style.display = "none";
    }else{
      document.getElementById('moreRead').style.display = "block";
    }
    //switch cat
  });
  function loadCategoryList(cat,lim,off){
    url = "http://em-home.appspot.com/getCategoryCommentList";
    req = {
      "name":"test",
      "category":cat,
      "limit":lim,
      "offset":off,
      "callback":"?"
    };
    $.post(url, req, callback,"json");
    var callback = function(json){
      if(json == 0){
        $('#listView').html("<p>まだコメントがありません</p>");
      }
      $.each(json, function(i, item) {
        resJson[i] = this;
        message = '<a href="#" data-transition="slide"><table class="comInfo"><tr>'
        + '<td><p class="date">'
        + formatDate(this.date.isoformat)
        + '</p><p class="comTitle"><h4>'
        + this.title
        + '</h4><p class="NI_data">読了目安:'
        + this.body
        + '</p><p 分'
        + '　閲覧数:'
        + this.views
        + '　★'
        + this.bookmark
        + '</p></td></tr></table></a> ';
        items++;
        //str = str + message;
        $('<li>').html(message).appendTo('#listView');
        message = "";
      });
    };
  };
});
//list終わり

//時間変換のファンクション
function utc2jst(utc) {
  return new Date(utc.getTime() + 9*60*60*1000);
} 
function formatDate(date){
  var userAgent = window.navigator.userAgent.toLowerCase();
  var appVersion = window.navigator.appVersion.toLowerCase();
  jst = date;
  if (userAgent.indexOf("firefox") > -1) {
    jst = utc2jst(date);
  }
  var created_at = date.toString().split(" ");
  if(created_at[1] == "Jan") created_at[1] = "01";
  if(created_at[1] == "Feb") created_at[1] = "02";
  if(created_at[1] == "Mar") created_at[1] = "03";
  if(created_at[1] == "Apr") created_at[1] = "04";
  if(created_at[1] == "May") created_at[1] = "05";
  if(created_at[1] == "Jun") created_at[1] = "06";
  if(created_at[1] == "Jul") created_at[1] = "07";
  if(created_at[1] == "Aug") created_at[1] = "08";
  if(created_at[1] == "Sep") created_at[1] = "09";
  if(created_at[1] == "Oct") created_at[1] = "10";
  if(created_at[1] == "Nov") created_at[1] = "11";
  if(created_at[1] == "Dec") created_at[1] = "12";
  
  var post_date  = String(created_at[3]) + "/"
    + String(created_at[1]) + "/"
    + String(created_at[2]) + " "
    + String(created_at[4]);
  return String(post_date);
};
//時間変換のファンクションおわり

$.widget('mobile.tabbar', $.mobile.navbar, {
  _create: function() {
    // Set the theme before we call the prototype, which will 
    // ensure buttonMarkup() correctly grabs the inheritied theme.
    // We default to the "a" swatch if none is found
    var theme = this.element.jqmData('theme') || "a";
    this.element.addClass('ui-footer ui-footer-fixed ui-bar-' + theme);

    // Make sure the page has padding added to it to account for the fixed bar
    this.element.closest('[data-role="page"]').addClass('ui-page-footer-fixed');


    // Call the NavBar _create prototype
    $.mobile.navbar.prototype._create.call(this);
  },

  // Set the active URL for the Tab Bar, and highlight that button on the bar
  setActive: function(url) {
    // Sometimes the active state isn't properly cleared, so we reset it ourselves
    this.element.find('a').removeClass('ui-btn-active ui-state-persist');
    this.element.find('a[href="' + url + '"]').addClass('ui-btn-active ui-state-persist');
  }
});

$(document).bind('pagecreate create', function(e) {
  return $(e.target).find(":jqmData(role='tabbar')").tabbar();
});

$(":jqmData(role='page')").live('pageshow', function(e) {
  // Grab the id of the page that's showing, and select it on the Tab Bar on the page
  var tabBar, id = $(e.target).attr('id');

  tabBar = $.mobile.activePage.find(':jqmData(role="tabbar")');
  if(tabBar.length) {
    tabBar.tabbar('setActive', '#' + id);
  }
});

var attachEvents = function() {
var hoverDelay = $.mobile.buttonMarkup.hoverDelay, hov, foc;

$( document ).bind( {
	"vmousedown vmousecancel vmouseup vmouseover vmouseout focus blur scrollstart": function( event ) {
		var theme,
			$btn = $( closestEnabledButton( event.target ) ),
			evt = event.type;
	
		if ( $btn.length ) {
			theme = $btn.attr( "data-" + $.mobile.ns + "theme" );
	
			if ( evt === "vmousedown" ) {
				if ( $.support.touch ) {
					hov = setTimeout(function() {
						$btn.removeClass( "ui-btn-up-" + theme ).addClass( "ui-btn-down-" + theme );
					}, hoverDelay );
				} else {
					$btn.removeClass( "ui-btn-up-" + theme ).addClass( "ui-btn-down-" + theme );
				}
			} else if ( evt === "vmousecancel" || evt === "vmouseup" ) {
				$btn.removeClass( "ui-btn-down-" + theme ).addClass( "ui-btn-up-" + theme );
			} else if ( evt === "vmouseover" || evt === "focus" ) {
				if ( $.support.touch ) {
					foc = setTimeout(function() {
						$btn.removeClass( "ui-btn-up-" + theme ).addClass( "ui-btn-hover-" + theme );
					}, hoverDelay );
				} else {
					$btn.removeClass( "ui-btn-up-" + theme ).addClass( "ui-btn-hover-" + theme );
				}
			} else if ( evt === "vmouseout" || evt === "blur" || evt === "scrollstart" ) {
				$btn.removeClass( "ui-btn-hover-" + theme  + " ui-btn-down-" + theme ).addClass( "ui-btn-up-" + theme );
				if ( hov ) {
					clearTimeout( hov );
				}
				if ( foc ) {
					clearTimeout( foc );
				}
			}
		}
	},
	"focusin focus": function( event ){
		$( closestEnabledButton( event.target ) ).addClass( $.mobile.focusClass );
	},
	"focusout blur": function( event ){
		$( closestEnabledButton( event.target ) ).removeClass( $.mobile.focusClass );
	}
});

attachEvents = null;
};

$.fn.buttonMarkup = function( options ) {
var $workingSet = this;

// Enforce options to be of type string
options = ( options && ( $.type( options ) == "object" ) )? options : {};
for ( var i = 0; i < $workingSet.length; i++ ) {
	var el = $workingSet.eq( i ),
		e = el[ 0 ],
		o = $.extend( {}, $.fn.buttonMarkup.defaults, {
			icon:       options.icon       !== undefined ? options.icon       : el.jqmData( "icon" ),
			iconpos:    options.iconpos    !== undefined ? options.iconpos    : el.jqmData( "iconpos" ),
			theme:      options.theme      !== undefined ? options.theme      : el.jqmData( "theme" ) || $.mobile.getInheritedTheme( el, "c" ),
			inline:     options.inline     !== undefined ? options.inline     : el.jqmData( "inline" ),
			shadow:     options.shadow     !== undefined ? options.shadow     : el.jqmData( "shadow" ),
			corners:    options.corners    !== undefined ? options.corners    : el.jqmData( "corners" ),
			iconshadow: options.iconshadow !== undefined ? options.iconshadow : el.jqmData( "iconshadow" ),
			iconsize:   options.iconsize   !== undefined ? options.iconsize   : el.jqmData( "iconsize" ),
			mini:       options.mini       !== undefined ? options.mini       : el.jqmData( "mini" )
		}, options ),

		// Classes Defined
		innerClass = "ui-btn-inner",
		textClass = "ui-btn-text",
		buttonClass, iconClass,
		// Button inner markup
		buttonInner,
		buttonText,
		buttonIcon,
		buttonElements;

	$.each(o, function(key, value) {
		e.setAttribute( "data-" + $.mobile.ns + key, value );
		el.jqmData(key, value);
	});

	// Check if this element is already enhanced
	buttonElements = $.data(((e.tagName === "INPUT" || e.tagName === "BUTTON") ? e.parentNode : e), "buttonElements");

	if (buttonElements) {
		e = buttonElements.outer;
		el = $(e);
		buttonInner = buttonElements.inner;
		buttonText = buttonElements.text;
		// We will recreate this icon below
		$(buttonElements.icon).remove();
		buttonElements.icon = null;
	}
	else {
		buttonInner = document.createElement( o.wrapperEls );
		buttonText = document.createElement( o.wrapperEls );
	}
	buttonIcon = o.icon ? document.createElement( "span" ) : null;

	if ( attachEvents && !buttonElements) {
		attachEvents();
	}
	
	// if not, try to find closest theme container	
	if ( !o.theme ) {
		o.theme = $.mobile.getInheritedTheme( el, "c" );	
	}		

	buttonClass = "ui-btn ui-btn-up-" + o.theme;
	buttonClass += o.inline ? " ui-btn-inline" : "";
	buttonClass += o.shadow ? " ui-shadow" : "";
	buttonClass += o.corners ? " ui-btn-corner-all" : "";

	if ( o.mini !== undefined ) {
		// Used to control styling in headers/footers, where buttons default to `mini` style.
		buttonClass += o.mini ? " ui-mini" : " ui-fullsize";
	}
	
	if ( o.inline !== undefined ) {			
		// Used to control styling in headers/footers, where buttons default to `mini` style.
		buttonClass += o.inline === false ? " ui-btn-block" : " ui-btn-inline";
	}
	
	
	if ( o.icon ) {
		o.icon = "ui-icon-" + o.icon;
		o.iconpos = o.iconpos || "left";

		iconClass = "ui-icon " + o.icon;

		if ( o.iconshadow ) {
			iconClass += " ui-icon-shadow";
		}

		if ( o.iconsize ) {
			iconClass += " ui-iconsize-" + o.iconsize;
		}
	}

	if ( o.iconpos ) {
		buttonClass += " ui-btn-icon-" + o.iconpos;

		if ( o.iconpos == "notext" && !el.attr( "title" ) ) {
			el.attr( "title", el.getEncodedText() );
		}
	}
  
	innerClass += o.corners ? " ui-btn-corner-all" : "";

	if ( o.iconpos && o.iconpos === "notext" && !el.attr( "title" ) ) {
		el.attr( "title", el.getEncodedText() );
	}

	if ( buttonElements ) {
		el.removeClass( buttonElements.bcls || "" );
	}
	el.removeClass( "ui-link" ).addClass( buttonClass );

	buttonInner.className = innerClass;

	buttonText.className = textClass;
	if ( !buttonElements ) {
		buttonInner.appendChild( buttonText );
	}
	if ( buttonIcon ) {
		buttonIcon.className = iconClass;
		if ( !(buttonElements && buttonElements.icon) ) {
			buttonIcon.appendChild( document.createTextNode("\u00a0") );
			buttonInner.appendChild( buttonIcon );
		}
	}

	while ( e.firstChild && !buttonElements) {
		buttonText.appendChild( e.firstChild );
	}

	if ( !buttonElements ) {
		e.appendChild( buttonInner );
	}

	// Assign a structure containing the elements of this button to the elements of this button. This
	// will allow us to recognize this as an already-enhanced button in future calls to buttonMarkup().
	buttonElements = {
		bcls  : buttonClass,
		outer : e,
		inner : buttonInner,
		text  : buttonText,
		icon  : buttonIcon
	};

	$.data(e,           'buttonElements', buttonElements);
	$.data(buttonInner, 'buttonElements', buttonElements);
	$.data(buttonText,  'buttonElements', buttonElements);
	if (buttonIcon) {
		$.data(buttonIcon, 'buttonElements', buttonElements);
	}
}

return this;
};

$.fn.buttonMarkup.defaults = {
corners: true,
shadow: true,
iconshadow: true,
iconsize: 18,
wrapperEls: "span"
};

function closestEnabledButton( element ) {
  var cname;

  while ( element ) {
	// Note that we check for typeof className below because the element we
	// handed could be in an SVG DOM where className on SVG elements is defined to
	// be of a different type (SVGAnimatedString). We only operate on HTML DOM
	// elements, so we look for plain "string".
      cname = ( typeof element.className === 'string' ) && (element.className + ' ');
      if ( cname && cname.indexOf("ui-btn ") > -1 && cname.indexOf("ui-disabled ") < 0 ) {
          break;
      }

      element = element.parentNode;
  }

  return element;
}
