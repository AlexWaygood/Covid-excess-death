function WhileLoading(){
    $('.content').hide();
    $('#loading').show();
    document.body.style.cursor = 'wait';
}

function SocialShare(Network){
    var url = window.location.href;

    if (Network == "twitter"){
        var title = document.querySelector("meta[property='og:title']").getAttribute("content");
        var New_URL = "https://twitter.com/intent/tweet?text=" + title + "&url=" + url + "&via=CovidGraph"
    } else if (Network == 'facebook'){
        var New_URL = "https://www.facebook.com/sharer/sharer.php?u=" + url
    } else if (Network == 'linkedin'){
        var New_URL = "https://www.linkedin.com/sharing/share-offsite/?url=" + url
    } else{
        return ""
    }

    window.open(New_URL)
}
