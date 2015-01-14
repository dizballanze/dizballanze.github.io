/*
 * jQuery check password plug-in 1.0
 *
 * author lionasp
 * 
 * special for:
 * http://www.dizballanze.com
 *
 * params:
 * string maxIndicatorLength: '100px', '15%', ... - indicator length with strongest password
 * bool useAnimate
 * object indicatorField - DOM element, in which displays indicator
 */

(function($) {
    $.fn.strongPassword = function(params) {
	//default arguments
	var defaults = {maxIndicatorLength: '150px', useAnimate: true};
	var options = $.extend({}, defaults, params);
	
	if (options.indicatorField == undefined) {
	    $.error('Plugin jQuery.strongPassword: invalid argument value indicatorField');
	    return;
	}

	var useAnimate = !!options.useAnimate;
	
	var maxIndicatorLength = options.maxIndicatorLength;
	var NumericLength = maxIndicatorLength; 
	
	//check measure unit
	var measure = 'px';
	if (maxIndicatorLength.length > 2 && maxIndicatorLength.substr(-2) === 'px') {
	    NumericLength = maxIndicatorLength.substr(0, maxIndicatorLength.length - 2);
	} 
	else if (maxIndicatorLength.length > 1 && maxIndicatorLength.substr(-1) === '%') {
	    NumericLength = maxIndicatorLength.substr(0, maxIndicatorLength.length - 1);
	    measure = '%';
	} else {
	    $.error('Plugin jQuery.strongPassword: invalid argument value maxIndicatorLength');
	    return;
	}
	
	//one block length
	var FinalLength = NumericLength / 5;
	
	var indicator = options.indicatorField;
	
	//the initial state of the indicator
	indicator.css({
	    'background-color':'#ff0000',
	    'width':FinalLength  + measure,
	    'height':'10px',
	    'border-radius':'5px',
	    'margin':'5px'
	});
	
	//choice the function for change indicator size (with animation or not)
	var change_indicator_size;
	if (useAnimate === true) {
	    change_indicator_size = function(size) {
		indicator.animate({'width':size}, 'normal'); 
	    }
	} else {
	    change_indicator_size = function(size) {
		indicator.css({'width':size}); 
	    }
	}
	    

	$(this).keyup(function() {    
	    var pass = $(this).val();
	    var strong = 0;
	    
	    
	    if (pass.length >= 6) {
		if (/([0-9]+)/.test(pass)){ strong++; } // has digits?
		if (/([a-z]+)/.test(pass)){ strong++; } // ... lowercase letters?
		if (/([A-Z]+)/.test(pass)){ strong++; } // ... uppercase letters?
		if (/\W/.test(pass)){ strong++; }	// ... symbols?
	    }
	    
	    //changing the indicator on the complexity of the password
	    switch(strong) {
		case (0):
		    change_indicator_size(FinalLength + measure);
		    indicator.css({'background-color':'#ff0000'});
		    break;
		    
		case (1):
		    change_indicator_size((FinalLength * 2) + measure);
		    indicator.css({'background-color':'#ff0000'});
		    break;
		    
		case (2):
		    change_indicator_size((FinalLength * 3) + measure);
		    indicator.css({'background-color':'#edc422'});
		    break;
		    
		case (3):
		    change_indicator_size((FinalLength * 4) + measure);
		    indicator.css({'background-color':'#edc422'});
		    break;
		    
		case (4):
		    change_indicator_size((FinalLength * 5) + measure);
		    indicator.css({'background-color':'#2dda2f'});
		    break;
	    }
	});
    }
})(jQuery);
