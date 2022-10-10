function getMetaTag(name, content) {
    var metaTag = document.createElement('meta');
    metaTag.name = name;
    metaTag.content = content;
    return metaTag;
}

// function that adds a meta tag to the head of the document if it doesn't already exist
function addMetaTag(name, content) {
    var metaTags = document.getElementsByTagName('meta');
    for (var i = 0; i < metaTags.length; i++) {
        if (metaTags[i].name === name) {
            return;
        }
    }
    document.getElementsByTagName('head')[0].appendChild(getMetaTag(name, content));
}

addMetaTag(
    "Description",
    "Anime recommender system for Anilist user profiles and individual title(s).",
);

addMetaTag(
    "google-site-verification",
    "gld465HiecZa8jy-0b1iduTEp9Mg_hITVSqJpk35onQ",
);
