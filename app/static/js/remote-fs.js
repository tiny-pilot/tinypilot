document
  .getElementById("btn-remote-fs-ok")
  .addEventListener("click", submitRemoteFs);
document
  .getElementById("btn-remote-fs-cancel")
  .addEventListener("click", hideRemoteFsOverlay);
document
  .getElementById("remote-fs-share-type")
  .addEventListener("change", setSmbOptionsVisiblity);

document.getElementById("cdrom-msd-btn").addEventListener("click", () => {
  document
    .getElementById("file-browser-container")
    .setAttribute("data-msd-type", "cdrom");
  setFileSelectorPath("/");
  showFileSelectorOverlay();
});
document.getElementById("flash-msd-btn").addEventListener("click", () => {
  document
    .getElementById("file-browser-container")
    .setAttribute("data-msd-type", "flash");
  setFileSelectorPath("/");
  showFileSelectorOverlay();
});
document
  .getElementById("msd-file-selector-cancel")
  .addEventListener("click", () => {
    hideFileSelectorOverlay();
  });
document.getElementById("clear-msd-btn").addEventListener("click", () => {
  clearImage();
});
function showFileSelectorOverlay() {
  document.getElementById("msd-file-selector").setAttribute("show", "true");
}
function hideFileSelectorOverlay() {
  document.getElementById("msd-file-selector").setAttribute("show", "false");
}

function setFileSelectorPath(path) {
  document.getElementById("file-selector-path").innerText = path;

  let route = "/getRemoteFsContent?subPath=" + path;
  route = encodeURI(route);
  var data = fetch(route, {
    method: "GET",
    headers: {
      "X-CSRFToken": getCsrfToken(),
    },
    mode: "same-origin",
    cache: "no-cache",
    redirect: "error",
    body: data,
  })
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      var container = document.getElementById("file-browser-container");
      var msdType = container.getAttribute("data-msd-type");
      while (container.lastElementChild) {
        container.removeChild(container.lastElementChild);
      }
      if (data.success == true) {
        if (data.data.length > 0) {
          data.data[0].forEach((element) => {
            container.appendChild(
              createFileSelectorElement("folder", element, path, msdType)
            );
          });
          data.data[1].forEach((element) => {
            container.appendChild(
              createFileSelectorElement("file", element, path, msdType)
            );
          });
        }
      } else {
        alert(data.error);
      }
    });
}

function createFileSelectorElement(type, Name, currentPath, msdType) {
  if (type == "folder") Name = Name + "/";
  var ulObject = document.createElement("UL");
  ulObject.className = "ul-table";
  /*var liImgObject = document.createElement("LI");
  liImgObject.className = "img";
  var img = document.createElement("IMG");
  if (type == "folder") img.setAttribute("src", "img/folder-icon.png");
  else img.setAttribute("src", "img/file-icon.png");
  img.setAttribute("width", "16");
  img.setAttribute("height", "16");
  liImgObject.appendChild(img);
  ulObject.appendChild(liImgObject);*/
  var liTextObject = document.createElement("LI");
  liTextObject.innerText = Name;
  ulObject.appendChild(liTextObject);
  if (type == "folder") {
    ulObject.addEventListener("click", () => {
      setFileSelectorPath(currentPath + Name);
    });
  }
  if (type == "file") {
    ulObject.addEventListener("click", () => {
      mountImage(currentPath + Name, msdType);
    });
  }
  ulObject.setAttribute("data-path", currentPath + Name);
  return ulObject;
}

function mountImage(ImagePath, msdType) {
  let route = "/MountImage?Path=" + ImagePath + "&type=" + msdType;
  route = encodeURI(route);
  var data = fetch(route, {
    method: "GET",
    headers: {
      "X-CSRFToken": getCsrfToken(),
    },
    mode: "same-origin",
    cache: "no-cache",
    redirect: "error",
    body: data,
  })
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      if (data.success == false) {
        alert("Mount failed. " + data.error);
      }
      hideFileSelectorOverlay();
    });
}

function clearImage() {
  let route = "/ClearImage";
  route = encodeURI(route);
  var data = fetch(route, {
    method: "GET",
    headers: {
      "X-CSRFToken": getCsrfToken(),
    },
    mode: "same-origin",
    cache: "no-cache",
    redirect: "error",
    body: data,
  })
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      if (data.success == false) {
        alert("Unmount failed. " + data.error);
      } else {
        alert("Selected Image successfully unmounted");
      }
      hideFileSelectorOverlay();
    });
}

function showRemoteFsOverlay() {
  document
    .getElementById("remote-share-mount-selector")
    .setAttribute("show", "true");
  setSmbOptionsVisiblity();
}
function hideRemoteFsOverlay() {
  document
    .getElementById("remote-share-mount-selector")
    .setAttribute("show", "false");
}

function isRemoteFsShowing() {
  return (
    document
      .getElementById("remote-share-mount-selector")
      .getAttribute("show") === "true"
  );
}
function getCsrfToken() {
  return document
    .querySelector("meta[name='csrf-token']")
    .getAttribute("content");
}
function copyToClipboard(text) {
  var dummy = document.createElement("textarea");
  // to avoid breaking orgain page when copying more words
  // cant copy when adding below this code
  // dummy.style.display = 'none'
  document.body.appendChild(dummy);
  //Be careful if you use texarea. setAttribute('value', value), which works with "input" does not work with "textarea". – Eduard
  dummy.value = text;
  dummy.select();
  document.execCommand("copy");
  document.body.removeChild(dummy);
}
function submitRemoteFs() {
  const data = new URLSearchParams();
  for (const pair of new FormData(document.getElementById("remoteFsForm"))) {
    data.append(pair[0], pair[1]);
  }
  let route = "/mountRemoteFs";
  fetch(route, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCsrfToken(),
    },
    mode: "same-origin",
    cache: "no-cache",
    redirect: "error",
    body: data,
  })
    .then((response) => {
      // A 502 usually means that nginx shutdown before it could process the
      // response. Treat this as success.
      if (response.status === 502) {
        return Promise.resolve({});
      }
      if (response.status !== 200) {
        // See if the error response is JSON.
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
          return response.json().then((data) => {
            return Promise.reject(new Error(data.error));
          });
        }
        return Promise.reject(new Error(response.statusText));
      }
      return response.json();
    })
    .then((result) => {
      if (result.success == false) {
        alert("Mount failed. Maybe an Image is currently in use?");
      }
      if (result.error) {
        return Promise.reject(new Error(result.error));
      }
    })
    .catch((error) => {
      // Depending on timing, the server may not respond to the shutdown request
      // because it's shutting down. If we get a NetworkError, assume the
      // shutdown succeeded.
      if (error.message.indexOf("NetworkError") >= 0) {
        return;
      }
    });
  hideRemoteFsOverlay();
}

function setSmbOptionsVisiblity() {
  var comboBox = document.getElementById("remote-fs-share-type");
  var selValue = comboBox.options[comboBox.selectedIndex].value;
  var elements = document.getElementsByClassName("remote-fs-smb-selected");
  if (selValue == "smb") {
    for (i = 0; i < elements.length; i++) {
      elements[i].setAttribute("show", "true");
    }
  }
  if (selValue == "nfs") {
    for (i = 0; i < elements.length; i++) {
      elements[i].setAttribute("show", "false");
    }
  }
}
