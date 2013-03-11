$(function () {
  "use strict";

  var Exhibition = Backbone.Model.extend({
    urlRoot: 'cucu'
  });

  var ExhibitionList = Backbone.Collection.extend({
    url: 'get',
    model: Exhibition,
    parse: function (json) {
      return json.data;
    }
  });

  var ExhibitionListView = Backbone.View.extend({
    tagName: "ul",
    el: $("#exhibition_list_template"),
    initialize: function () {
      var self = this;
      this.model = new ExhibitionList();

      this.model.fetch({ success: function () {
        self.render();
      }});
    },
    render: function () {
      _.each(this.model.models, function (orderable) {
        $(this.el).append(new ExhibitionView({model: orderable}).render().el)
      }, this);
      return this;
    }
  });

  var ExhibitionView = Backbone.View.extend({
    tagName: "li",
    template: _.template($('#exhibition_template').html()),
    render: function () {
      $(this.el)
        .html(this.template(this.model.toJSON()));
      return this;
    }
  });

  new ExhibitionListView();
});