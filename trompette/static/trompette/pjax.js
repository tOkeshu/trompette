(function() {
  var request = function(url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.onload = function(e) {
      callback(xhr.response);
    };

    xhr.open('GET', url, true);
    xhr.setRequestHeader('X-PJAX', 'True');
    xhr.send();
  };

  var Pjax = function(config) {
    this.config = config;
  };

  Pjax.prototype = {
    bindHandlers: function(root) {
      for (selector in this.config) {
        var target = this.config[selector];
        root.querySelectorAll(selector).forEach(function(element) {
          this._bindHandler(element, target);
        }.bind(this));
      }
    },

    _bindHandler: function(element, target) {
      element.addEventListener("click", function(event) {
        event.preventDefault()
        info = element.dataset.info
        this._loadContent(element, target, info);
      }.bind(this));
    },

    _loadContent: function(element, target, info) {
      request(element.href, function(html) {
        var column = document.querySelector(target);
        if (!column) {
          var container = document.querySelector("#columns");
          column = document.createElement("div")
          column.classList.add("column");
          column.id = target.substr(1);
          column.dataset.info = info
          container.append(column);

          var columns = document.querySelectorAll("#columns > .column");
          if (columns.length > 4) {
            columns[1].remove()
          }
        }

        column.innerHTML = html;
        this.bindHandlers(column);
      }.bind(this));
    },
  };

  var pjax = new Pjax({
    ".to-status": "#status",
    ".to-hashtag": "#tag-tl",
    ".to-account": "#user-tl",
    ".to-notifications": "#notifications"
  });

  pjax.bindHandlers(document);

  let topics = ["#hashtags"]
  topics = topics.map(function(topic) {
    return "topic=" + encodeURIComponent(topic);
  }).join('&');

  let source = new EventSource('/streaming/?' + topics);
  source.addEventListener('status', function(message) {
    let status = JSON.parse(message.data);

    let newStatus   = document.createElement("li");
    newStatus.innerHTML = status.content;

    if (status.following) {
      let homeTL = document.querySelector('#home-tl > ul');
      if (homeTL)
        homeTL.prepend(newStatus)
    }

    status.tags.forEach(function(tag) {
      let selector = '#tag-tl[data-info="' + tag + '"]> ul';
      let tag_tl = document.querySelector(selector);
      if (tag_tl)
        tag_tl.prepend(newStatus)
    });
  });

}())
