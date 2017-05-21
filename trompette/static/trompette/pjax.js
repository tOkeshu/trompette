(function() {
  // var onClick = function() {
  //   var element = this;
  //   var url = element.href;

  //   request(url, function(html) {
  //   });
  // }

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
        this._loadContent(element, target);
      }.bind(this));
    },

    _loadContent: function(element, target) {
      request(element.href, function(html) {
        var column = document.querySelector(target);
        if (!column) {
          var container = document.querySelector("#columns");
          column = document.createElement("div")
          column.classList.add("column");
          column.id = target.substr(1);
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
}())
