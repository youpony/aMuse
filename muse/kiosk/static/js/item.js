$(function () {
  "use strict";

  var Item = Backbone.Model.extend({
  });

  var ItemList = Backbone.Collection.extend({
    url: '/api' + window.urls['item'].replace('<%= pk_m =>', window.exhibition.pk),
    model: Item,
    parse: function (json) {
      return json.data;
    }
  });

  var ItemView = Backbone.View.extend({
    tagName: "div",
    className: "span4 well",
    template: _.template($('#item_template').html()),
    render: function () {
      var tmplData = this.model.toJSON();
      $(this.el).html(this.template(tmplData));
      return this;
    }
  });

  var ItemListView = Backbone.View.extend({
    tagName: "div",
    el: $("#item_list_template"),
    initialize: function () {
      var self = this;

      this.model = new ItemList();

      this.model.fetch({ success: function () {
        self.render();
      }});
    },
    render: function () {
      _.each(this.model.models, function (item, i) {
        $(this.el).append(new ItemView({model: item}).render().el);
        if (i % 3 === 0)
          $(this.el).addClass('row-fluid');
      }, this);
      return this;
    }
  });

  new ItemListView();
});
