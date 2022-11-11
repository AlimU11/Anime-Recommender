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

poly_coefs = [-8.57907695e-23,  4.89386193e-19, -1.20229649e-15,  1.66487265e-12,
    -1.42791084e-09,  7.84544028e-07, -2.75615359e-04,  5.96649761e-02,
    -7.22065596e+00,  3.80269854e+02];

poly_coefs_small_screen = [-2.78102118e-08, -6.05882435e-05,  7.50649852e-02, -3.52615509e-01];

function translateButton(button) {
    width = window.innerWidth;
    translation = 0;

    coefs = width > 210 ? poly_coefs : poly_coefs_small_screen;

    for (i = 0; i < coefs.length; i++) {
        translation += coefs[i] * width ** (coefs.length-1 - i);
    }

    button.style.transform = `translateX(${translation}rem)`;
}

function toRight(button) {
    main_card = document.getElementsByClassName('main-card')[0];
    main_card.style.transform = 'translateX(-100%)';

    translateButton(button);

    text = document.createElement('span');
    text.textContent = 'Search';

    button.replaceChild(text, button.firstChild);

    document.documentElement.style.setProperty('--rotation', '-180deg');

    main_column = document.getElementsByClassName('main-column')[0];
    settings_column = document.getElementsByClassName('settings-column')[0];

    main_column.style.display = 'hidden';
    settings_column.style.display = 'block';
}

function toLeft(button) {
    main_card = document.getElementsByClassName('main-card')[0];
    main_card.style.transform = 'translateX(0%)';
    button.style.transform = 'translateX(0)';

    text = document.createElement('span');
    text.textContent = 'Parameters';

    button.replaceChild(text, button.firstChild);

    document.documentElement.style.setProperty('--rotation', '0deg');

    main_column = document.getElementsByClassName('main-column')[0];
    settings_column = document.getElementsByClassName('settings-column')[0];

    main_column.style.display = 'block';
    settings_column.style.display = 'none';
}

var functions = [toRight, toLeft];
var nextFunction = 0;

function functionSwitcher(button) {
    functions[nextFunction](button);
    nextFunction = (nextFunction + 1) % 2;
}

function onWindowResize() {
    document.documentElement.style.setProperty('--window-width', window.innerWidth + 'px');
    document.documentElement.style.setProperty('--graph-margin', -0.00742*window.innerWidth + 1.3137 + 'rem');
    var button = document.getElementsByClassName('header-container')[0].getElementsByTagName('button')[0];

    if (window.innerWidth <= 1100) {
        document.getElementsByClassName('settings-column')[0].classList.remove('col-4');
        document.getElementsByClassName('main-column')[0].classList.remove('col-8');
        document.getElementsByClassName('main-column')[0].classList.add('col-12');


        button.style.display = 'block';
        button.onclick = functionSwitcher.bind(null, button);

        if ((nextFunction + 1) % 2 == 0) {
            translateButton(button);
        }

        accordion = document.querySelector('.settings-accordion').querySelector('.accordion');

        Array.from(accordion.children).forEach((child) => {
            header = child.firstChild;
            body = header.nextSibling;
            body.classList.add('accordion-collapse', 'collapse', 'show');
        });
    }
    else {
        toLeft(button);
        nextFunction = 0;

        document.getElementsByClassName('settings-column')[0].classList.add('col-4');
        document.getElementsByClassName('main-column')[0].classList.remove('col-12');
        document.getElementsByClassName('main-column')[0].classList.add('col-8');

        var button = document.getElementsByClassName('header-container')[0].getElementsByTagName('button')[0];
        button.style.display = 'none';
        toLeft(button);

        accordion = document.querySelector('.settings-accordion').firstChild;

        accordion.children[0].firstChild.nextSibling.classList.add('show');
    }
};

window.onresize = onWindowResize;

document.addEventListener('DOMContentLoaded', function() {
    onWindowResize();
 }, false);

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        resizeOnPageLoad: function(_) {
            onWindowResize();
        }
    }
});
