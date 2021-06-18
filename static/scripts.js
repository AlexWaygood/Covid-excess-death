function WhileLoading(){
    $('.content').hide();
    $('.loading').show();
    document.body.style.cursor = 'wait';
}

function TwitterShare(){
    var title = document.querySelector("meta[property='og:title']").getAttribute("content");
    window.open("https://twitter.com/intent/tweet?text=" + title + "&url=" + window.location.href + "&via=CovidGraph");
}

function FacebookShare(){
    window.open("https://www.facebook.com/sharer/sharer.php?u=" + window.location.href);
}

function LinkedInShare(){
    window.open("https://www.linkedin.com/shareArticle?mini-true&url=" + window.location.href);
}

function CopyLinkToClipboard(){
    navigator.clipboard.writeText(window.location.href);
}

function AddSocialShareLinks(){
    document.getElementById("Twitter_icon").addEventListener("click", TwitterShare);
    document.getElementById("Facebook_icon").addEventListener("click", FacebookShare);
    document.getElementById("LinkedIn_icon").addEventListener("click", LinkedInShare);
    document.getElementById("clipboard_copy_icon").addEventListener("click", CopyLinkToClipboard);
}

function HamburgerMenu() {
    $('#nav_btn').click(function(e) {
        if($('.MobileMenu').is(':hidden') == true) {
            $(this).toggleClass("active");
            $('.MobileMenu').removeClass("toggle");
        } else {
            $(this).removeClass("active");
            $('.MobileMenu').addClass("toggle");
        }
        e.preventDefault();
    });
}