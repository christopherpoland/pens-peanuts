discernPhotoType();
activePage();

document.addEventListener("click", function(event) {
  if (event.target.id === "expandIcon" && event.target.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.querySelector(".expanded-content").classList.contains('hidden')) { //.preview-box is hidden
    event.target.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.querySelector(".preview-box").classList.toggle('hidden'); //.preview-box
    event.target.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.querySelector(".expanded-content").classList.toggle('hidden'); //.expanded-content
    event.target.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.querySelector(".expanded-content").scrollIntoView(); //moves viewport back to collapsed element
    }
  else if (event.target.id === "collapseIcon" && event.target.parentElement.parentElement.parentElement.parentElement.querySelector(".preview-box").classList.contains('hidden')) { //.preview-box is hidden
    event.target.parentElement.parentElement.parentElement.parentElement.querySelector(".preview-box").classList.toggle('hidden'); //.preview-box
    event.target.parentElement.parentElement.parentElement.parentElement.querySelector(".expanded-content").classList.toggle('hidden'); //.expanded-content
    event.target.parentElement.parentElement.parentElement.parentElement.querySelector(".preview-box").scrollIntoView(); //moves viewport back to collapsed element
  }
});
document.getElementById("smallNav").addEventListener("click", function(event) { //Opens or exits modal
  modalDisplay(event);
  document.body.style.overflow = "hidden";
});
document.addEventListener("click", function(event) { //Exits Modal
  if (event.target.id === "navbarWrapper") {
    modalDisplay(event);
    expandModal();
  }
});
/*document.getElementById("nameInput").addEventListener("click", function(event) {
  expandModal();
});
document.getElementById("emailInput").addEventListener("click", function(event) {
  expandModal();
});
document.getElementById("messageInput").addEventListener("click", function(event) {
  expandModal();
}); */

/* BLURB ACTIVITY */
if (location.pathname == "/") { //Refers to homepage which has '/' as end of file name
    document.getElementsByClassName('section-blurb')[0].style.display = "grid";
  }
blurb = document.getElementsByClassName('section-blurb')[0];
if (blurb && document.getElementById("info")) {
  document.getElementById("info").addEventListener("click", function(event) {
    if (window.getComputedStyle(blurb).display === "none") { //display modal
      document.getElementsByClassName('section-blurb')[0].style.display = "grid";
    }
    else {
      document.getElementsByClassName('section-blurb')[0].style.display = "none";
    }
  });
}
if (document.getElementById("closeIntro")) {
  document.getElementById("closeIntro").addEventListener("click", function(event) {
      document.getElementsByClassName('section-blurb')[0].style.display = "none";
  });
}
if (document.getElementById("closeFlash")) {
  document.getElementById("closeFlash").addEventListener("click", function(event) {
      document.getElementsByClassName('flash-wrapper')[0].style.display = "none";
  });
}


function modalDisplay(event) {
    var modal = document.getElementById("navbarWrapper");
    var header = document.getElementById("header");
    var titleNames = ["Pens","Pages","People","Places","Peanuts"];
    if (window.getComputedStyle(modal).display === "none") { //display modal
      modal.style.display = "flex";
      document.getElementById("close").style.display = "block";
      document.getElementById("navbar").style.display = "grid";
      document.getElementById("close").style.display = "block";
      document.getElementById("menu").style.display = "none";

    }
    else { //hides modal
      modal.style.display = "none";
      document.body.style.overflow = "auto";
      navbar.classList.remove('navbar-extend');
      navbar.classList.add('navbar-initial');
      document.getElementById("close").style.display = "none";
      document.getElementById("navbar").style.display = "none";
      document.getElementById("menu").style.display = "block";
      //document.getElementById("contactMobile").classList.remove("contact-mobile-extended");
      navbar.querySelectorAll("a").forEach((element,index) => {
        element.style.textAlign = "left";
        element.innerHTML = titleNames[index];
      });
    }
}
function expandModal() {
  var navbar = document.getElementById("navbar");
  var emojis = ["🖊️","📖","👪","⛺","🌰"];
  //Check if width is 40% or 90%
  if (Math.round((window.getComputedStyle(navbar).width).replace("px","")) === Math.round(window.innerWidth * 0.4)) { //expands
    navbar.classList.add('navbar-extend');
    navbar.classList.remove('navbar-initial');
    document.getElementById("contactMobile").classList.add("contact-mobile-extended");

    navbar.querySelectorAll("a").forEach((element,index) => {
      element.style.textAlign = "center";
      element.innerHTML = emojis[index];
    });
  }
}
function discernPhotoType() {
  var previewPhotos = document.querySelectorAll(".preview-photo");
  previewPhotos.forEach(element => {
    var height = window.getComputedStyle(element).height;
    var width = window.getComputedStyle(element).width;
    if (height > width) {
      element.classList.add('portrait');
    }
    else {
      element.classList.add('landscape')
    }
  });
}
function activePage() {
  navbar = document.getElementById("navbar");
  pageTitle = document.getElementById("pageTitle");
  navbar.querySelectorAll("a").forEach((element) => {
    if (pageTitle && element.textContent === pageTitle.textContent) {
      if (document.documentElement.clientWidth >= 500)
        element.style.backgroundColor = "white";
      else {
        element.style.backgroundColor = "#6cb";
      }
      element.style.color = "black";
    }
  });
}
