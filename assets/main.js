function getMetaTag(name, content) {
    var metaTag = document.createElement('meta');
    metaTag.name = name;
    metaTag.content = content;
    return metaTag;
}

document.getElementsByTagName('head')[0].appendChild(getMetaTag(
    "Description",
    "Anime recommender system for Anilist user profiles and individual title(s).",
));

document.getElementsByTagName('head')[0].appendChild(getMetaTag(
    "google-site-verification",
    "gld465HiecZa8jy-0b1iduTEp9Mg_hITVSqJpk35onQ",
));
