$(function () {
  "use strict";

  var Item = Backbone.Model.extend({
  });

  window.ItemDetail = Backbone.Model.extend({
    urlRoot: window.urls['item'],
    parse: function (json) {
      return json.data;
    }
  });

  var ItemList = Backbone.Collection.extend({
    url: window.urls['exhibitionitem'].replace('<%= pk_m =>', window.exhibition.pk),
    model: Item,
    parse: function (json) {
      return json.data;
    }
  });

  var ItemView = Backbone.View.extend({
    tagName: "div",
    className: "span4 well item",
    template: _.template($('#item_template').html()),
    render: function () {
      var tmplData = this.model.toJSON();
      $(this.el).html(this.template(tmplData));
      return this;
    }
  });

  var ItemDetailView = Backbone.View.extend({
    template: _.template($('#item_detail_template').html()),
    initialize: function (data) {
      var self = this;

      this.model = new ItemDetail({id: data['pk']});
      this.model.fetch({success: function (data) {
        self.model.set(data.attributes);
        self.render();
      }})
    },
    render: function () {
      var tmplData = this.model.toJSON();
      $('#item_detail_template_placeholder').html($(this.el).html(this.template(tmplData)));
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
    events: {
      "click .item": "showItemDetails"
    },
    showItemDetails: function (event) {
      var $this = $(event.currentTarget);
      new ItemDetailView({pk: $this.children().data('pk')});
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
