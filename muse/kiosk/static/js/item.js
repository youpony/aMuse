/* jshint undef: true */
/* global Backbone: true, _: true */

$(function () {
  "use strict";

  var Item = Backbone.Model.extend({
      defaults: {
        images: []
      }
    })

    , ItemDetail = Backbone.Model.extend({
      urlRoot: window.urls.item,
      parse: function (json) {
        return json.data;
      }
    })

    , ItemList = Backbone.Collection.extend({
      url: window.urls.exhibitionitem.replace('<%= pk_m =>', window.exhibition.pk),
      model: Item,
      parse: function (json) {
        return json.data;
      }
    })

    , ItemView = Backbone.View.extend({
      tagName: "div",
      className: "item",
      template: _.template($('#item_template').html()),
      events: {
        'click .icon-star': 'changeStarStatus'
      },
      changeStarStatus: function (e) {
        var $this = $(e.target)
          , $parent = $this.closest('article')
          , $endButton = $('#end-button');

        e.preventDefault();
        e.stopPropagation();
        $this.toggleClass('icon-star-active');

        $('article[data-pk=' + $parent.data('pk') + ']:not(.item)')
          .find('.icon-star').toggleClass('icon-star-active');

        if ($('.icon-star-active').length > 0)
          $endButton.show();
        else $endButton.hide();
      },
      render: function () {
        var tmplData = this.model.toJSON();
        $(this.el).html(this.template(tmplData));
        return this;
      }
    })

    , ItemDetailView = Backbone.View.extend({
      template: _.template($('#item_detail_template').html()),
      initialize: function (data) {
        var self = this;

        this.model = new ItemDetail({id: data.pk});

        this.model.fetch({success: function (data) {
          self.model.set(data.attributes);
          self.render();
        }});
      },
      events: {
        'click .icon-star': 'changeStarStatus',
        'click #close-button': 'closeDetailView',
        'click .other-images': 'changeImage'
      },
      changeStarStatus: function (e) {
        var $this = $(e.target)
          , $parent = $this.closest('article')
          , $endButton = $('#end-button');

        e.preventDefault();
        e.stopPropagation();
        $this.toggleClass('icon-star-active');

        $('article[data-pk=' + $parent.data('pk') + ']:not(.item-detail)')
          .find('.icon-star').toggleClass('icon-star-active');

        if ($('.icon-star-active').length > 0)
          $endButton.show();
        else $endButton.hide();
      },
      closeDetailView: function (e) {
        $('#main').removeClass('slide-left');
        $('#sidebar-detail').removeClass('slide-left');
      },
      changeImage: function (e) {
        var $this = $(e.target);
        $('.first-image').attr('src', $this.attr('src'));
      },
      render: function (e) {
        var $this = $(this.el)
          , $star = $('article[data-pk=' + this.model.id + ']')
          , tmplData = $.extend({}, this.model.toJSON(), {'active': $star.find('i').is('.icon-star-active')});
        $('#sidebar-detail').html($this.html(this.template(tmplData)));
        return this;
      }
    })

    ,
    ItemListView = Backbone.View.extend({
      tagName: "div",
      el: $("#item-list-template"),
      initialize: function () {
        var self = this;

        this.model = new ItemList();

        this.model.fetch({ success: function () {
          self.render();
        }});
      },
      events: {
        "click div.item": "showItemDetails"
      },
      showItemDetails: function (event) {
        var $this = $(event.currentTarget);

        $('#main').addClass('slide-left');
        $('#sidebar-detail').addClass('slide-left');

        new ItemDetailView({pk: $this.children().data('pk')});
      },
      render: function () {
        _.each(this.model.models, function (item) {
          $(this.el).append(new ItemView({model: item}).render().el);
        }, this);
        return this;
      }
    })

    , ExhibitionDetail = Backbone.Model.extend({
      url: window.urls.exhibition.replace('<%= pk_m =>', window.exhibition.pk)
    })

    , ExhibitionDetailView = Backbone.View.extend({
      tagName: "div",
      el: $("#exhibition-detail"),
      template: _.template($('#exhibition_detail_template').html()),
      initialize: function () {
        var self = this;

        this.model = new ExhibitionDetail();
        this.model.fetch({success: function () {
          $('#wrapper').tubular({
            videoId: self.model.get('video'),
            mute: true,
            repeat: true,
            start: 10
          });

          self.render();
        }});

      },
      events: {
        "click #back-button": 'backButtonClick',
        "click #end-button": 'endButtonClick'
      },
      backButtonClick: function (e) {
        var $endExhibitionForm = $('#end_exhibition_form');

        if ($endExhibitionForm.is(':hidden'))
          window.location.href = window.urls.kiosk;
        else {
          $('#item-list-template, #item_detail_template_placeholder').show();
          $('#end-button').show();
          $endExhibitionForm.hide();
        }
      },
      endButtonClick: function (e) {
        var startCounter = $('.icon-star-active').length;
        $(this).hide();
        $('#item-list-template, #item_detail_template_placeholder').hide();
        $('#end_exhibition_form').show();
      },
      render: function () {
        var tmplData = this.model.toJSON();
        $(this.el).html(this.template(tmplData));
        return this;
      }
    });

  new ItemListView();
  new ExhibitionDetailView();
})
;
