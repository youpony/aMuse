/* jshint undef: true */
/* global Backbone: true, _: true */

$(function () {
  "use strict";

  var Exhibition = Backbone.Model.extend({
      defaults: {
        image: ""
      }
    })

    , ExhibitionList = Backbone.Collection.extend({
      url: window.urls.exhibitions,
      model: Exhibition,
      parse: function (json) {
        return json.data;
      }
    })

    , ExhibitionView = Backbone.View.extend({
      tagName: "div",
      className: "pin",
      template: _.template($('#exhibition_template').html()),
      render: function () {
        var tmplData = {}
          , attr = this.model.attributes;

        $.extend(tmplData, attr, {'url': window.urls.kiosk + attr.pk});
        $(this.el).html(this.template(tmplData));
        return this;
      }
    })

    , ExhibitionListView = Backbone.View.extend({
      tagName: "div",
      el: $("#exhibition-list-template"),
      initialize: function () {
        var self = this;

        this.model = new ExhibitionList();

        this.model.fetch({ success: function () {
          $('body').css('background-image', 'url(http://crisdecuba.com/images/background1920x1080.jpg)')
          self.render();
        }});
      },
      render: function () {
        _.each(this.model.models, function (exhibition, i) {
          $(this.el).append(new ExhibitionView({model: exhibition}).render().el);
          if (i % 3 === 0)
            $(this.el).addClass('row-fluid');
        }, this);
        return this;
      }
    });

  new ExhibitionListView();
});
