$(function () {
  "use strict";

  var Exhibition = Backbone.Model.extend({
    urlRoot: 'cucu'
  });

  var ExhibitionList = Backbone.Collection.extend({
    url: '/api/m',
    model: Exhibition,
    parse: function (json) {
      return json.data;
    }
  });

  var ExhibitionView = Backbone.View.extend({
    tagName: "div",
    className: "span4 well",
    template: _.template($('#exhibition_template').html()),
    render: function () {
      $(this.el).html(this.template(this.model.toJSON()));
      return this;
    }
  });

  var ExhibitionListView = Backbone.View.extend({
    tagName: "div",
    el: $("#exhibition_list_template"),
    initialize: function () {
      var self = this;

      this.model = new ExhibitionList();

      this.model.fetch({ success: function () {
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
