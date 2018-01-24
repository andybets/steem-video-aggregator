import Vue from 'vue'
import BootstrapVue from "bootstrap-vue"
import VueRouter from 'vue-router'
import vueResource from 'vue-resource'
import HomePage from './HomePage.vue'
import PlayPage from './PlayPage.vue'
import SearchResultsPage from './SearchResultsPage.vue'
import ThumbnailsPage from './ThumbnailsPage.vue'
import HeaderBar from './HeaderBar.vue'
import PlayerYoutube from './PlayerYoutube.vue'
import PlayerDtube from './PlayerDtube.vue'
import PlayerDlive from './PlayerDlive.vue'
import RepliesPanel from './RepliesPanel.vue'

import "bootstrap/dist/css/bootstrap.min.css"
import "bootstrap-vue/dist/bootstrap-vue.css"

import VueCarousel from 'vue-carousel';
import InfiniteLoading from 'vue-infinite-loading';

Vue.use(BootstrapVue);
Vue.use(vueResource);
Vue.use(VueRouter);
Vue.use(VueCarousel);

var Icon = require('vue-awesome');
Vue.component('icon', Icon);
Vue.component('infinite-loading', InfiniteLoading);

Vue.component('player-youtube', PlayerYoutube);
Vue.component('player-dtube', PlayerDtube);
Vue.component('player-dlive', PlayerDlive);
Vue.component('replies-panel', RepliesPanel);

export const bus = new Vue();

// steemconnect v2 libraries
var s1 = require('./assets/template/js/sc2.min.js');
var s2 = require('./assets/template/js/steem.min.js');

// directive to trigger actions primarily if clicking outside header bar
Vue.directive('click-outside', {
  bind: function (el, binding, vnode) {
    el.event = function (event) {
      // here I check that click was outside the el and his childrens
      if (!(el == event.target || el.contains(event.target))) {
        // and if it did, call method provided in attribute value
        vnode.context[binding.expression](event);
      }
    };
    document.body.addEventListener('click', el.event)
  },
  unbind: function (el) {
    document.body.removeEventListener('click', el.event)
  },
});

// plugin to store global app state
const globals = new Vue({
    data: function() {
        return {
            loggedIn: true,
            username: 'Guest',
            userImageURL: null,
            token: null,
            cookiesAccepted: true,
            Icon: require('vue-awesome'),

            search_terms: '',
            filter_age_selection: 'all',
            filter_type_selection: 'all',
            filter_duration_selection: 'all',
            filter_sort_selection: 'date',            

            filter_exclude_old_video: 'true',
            filter_exclude_nsfw: 'true',
            filter_reputation_active: 'false',
            filter_quick_play_enabled: 'false',

            filter_not_default: false,
            preferences_not_default: false

        }
    },
    watch: {
        filter_age_selection: function() { this.saveFilterValues() },
        filter_type_selection: function() { this.saveFilterValues() },
        filter_duration_selection: function() { this.saveFilterValues() },
        filter_sort_selection: function() { this.saveFilterValues() },
        filter_exclude_old_video: function() { this.saveFilterValues() },
        filter_exclude_nsfw: function() { this.saveFilterValues() },
        filter_reputation_active: function() { this.saveFilterValues() },
        filter_quick_play_enabled: function() { this.saveFilterValues() }
    },
    created: function() {
        // load filter preferences from local storage
        this.loadFilterValues();

        sc2.init({
          baseURL: 'https://v2.steemconnect.com',
          app: 'multitube.app',
          callbackURL: 'http://localhost',
          scope: ['vote', 'comment']
        });

        if (localStorage.getItem("cookiesAccepted") === null) {
            this.cookiesAccepted = false;
        }

        if (localStorage.getItem("username") === null) {
            this.loggedIn = false;
        } else {
            this.username = localStorage.getItem("username");
            this.token = localStorage.getItem("token");
            this.userImageURL = localStorage.getItem("userImageURL");
            this.completeLogin(this.token);
        }

      },
    methods: {
        startLogin: function() {
            return // todo - remove to start integrating steemconnect
            window.location.href = sc2.getLoginURL();
        },
        completeLogin: function(access_token) { // from this.$route.query.access_token
              this.loggedIn = true; // hide login button, unless there's a login error
              sc2.setAccessToken(access_token);
              var t = this;
              sc2.me(function (err, result) {
                if (!err) {
//                  var user = result.account;
//                  var metadata = JSON.stringify(result.user_metadata, null, 2);
//                  console.log(result);
                    t.username = result.account.name;
                    t.token = access_token;
                    t.userImageURL = JSON.parse(result.account.json_metadata).profile.profile_image;
                    localStorage.setItem("username", result.account.name);
                    localStorage.setItem("token", access_token);
                    localStorage.setItem("userImageURL", 'access_token');
                    t.loggedIn = true;
                    // todo remove long return url querystring after steemconnect redirect
//                    router.replace('/');
//                    router.replace(getPathFromUrl(window.location.href));
//                    console.log(user);
//                    console.log(metadata);
                } else {
                    t.loggedIn = false;
                    localStorage.clear();
                    console.log(err);
                }
              });
        },
        vote: function(author, permlink, weight, success_callback, error_callback) {
            sc2.vote(this.username, author, permlink, weight, function (err, res) {
                console.log(err, res);
                if (!err) {
                    success_callback();
                } else {
                    error_callback(err);
                }
            });
        },
        comment: function(parentAuthor, parentPermlink, author, permlink, title, body, jsonMetadata, success_callback, error_callback) {
            sc2.comment(parentAuthor, parentPermlink, author, permlink, title, body, jsonMetadata, function (err, res) {
                console.log(err, res)
                if (!err) {
                    success_callback();
                } else {
                    error_callback(err);
                }
            });            
        },
        saveFilterValues: function() {
            // update state of filters for visual indications
            if ((this.filter_age_selection != 'all') || (this.filter_type_selection != 'all') 
                || (this.filter_duration_selection != 'all') || (this.filter_sort_selection != 'date') ) {
                this.filter_not_default = true;
            } else {
                this.filter_not_default = false;
            }

            // update state of preferences for visual indications
            if ((this.filter_exclude_old_video != 'true') || (this.filter_exclude_nsfw != 'true') ) {
                this.preferences_not_default = true;
            } else {
                this.preferences_not_default = false;
            }

            localStorage.setItem('filter_age_selection', this.filter_age_selection);
            localStorage.setItem('filter_type_selection', this.filter_type_selection);
            localStorage.setItem('filter_duration_selection', this.filter_duration_selection);
            localStorage.setItem('filter_sort_selection', this.filter_sort_selection);
            localStorage.setItem('filter_exclude_old_video', this.filter_exclude_old_video);
            localStorage.setItem('filter_exclude_nsfw', this.filter_exclude_nsfw);
            localStorage.setItem('filter_reputation_active', this.filter_reputation_active);
            localStorage.setItem('filter_quick_play_enabled', this.filter_quick_play_enabled);
            bus.$emit('filtersChanged'); // todo - prevent this firing several time on initial fetch if it does
        },
        loadFilterValues: function() {
            if (localStorage["filter_exclude_old_video"]) { // all saved when one is, so just need to check one
                this.filter_age_selection = localStorage['filter_age_selection'];
                this.filter_type_selection = localStorage['filter_type_selection'];
                this.filter_duration_selection = localStorage['filter_duration_selection'];
                this.filter_sort_selection = localStorage['filter_sort_selection'];
                this.filter_exclude_old_video = localStorage['filter_exclude_old_video'];
                this.filter_exclude_nsfw = localStorage['filter_exclude_nsfw'];
                this.filter_reputation_active = localStorage['filter_reputation_active'];
                this.filter_quick_play_enabled = localStorage['filter_quick_play_enabled'];
            }
        }
    }
})
globals.install = function(){
  Object.defineProperty(Vue.prototype, '$globals', {
    get () { return globals }
  })
}
Vue.use(globals);

// This code loads the YouTube IFrame Player API code asynchronously, and makes available globally
var tag = document.createElement('script');
tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
var cmp = this;
window.youtubeAPIReady = false;
window.onYouTubeIframeAPIReady = function() {
    window.youtubeAPIReady = true;
}

const router = new VueRouter({
    mode: 'history',
    base: __dirname,
    routes: [
        { path: '/', component: HomePage },
        { path: '/@:author/:permlink', component: PlayPage },
        { path: '/search/:search_terms', component: SearchResultsPage },
        { path: '/trending', component: ThumbnailsPage, props: { 
            page_title: 'Trending Videos', 
            video_list_url: '/f/api/trending-videos' }},
        { path: '/hot', component: ThumbnailsPage, props: { 
            page_title: 'Hot Videos', 
            video_list_url: '/f/api/hot-videos' }},
        { path: '/new', component: ThumbnailsPage, props: { 
            page_title: 'New Videos', 
            video_list_url: '/f/api/new-videos' }}
    ],
});

new Vue({
  router,
  components: {
    'header-bar': HeaderBar 
  },
  data: function() {
        return {
            showDismissibleAlert: true
        }
    },
  methods: {
    hideCookieNotice: function() {
        this.showDismissibleAlert=false;
        localStorage.setItem("cookiesAccepted", 'Yes');
    }
  },
  template: `
        <div id="app">
            <b-alert variant="warning" v-if="!$globals.cookiesAccepted" style="margin-bottom:3px" dismissible :show="showDismissibleAlert" @dismissed="hideCookieNotice">
            <h5>
            Using multi.tube means you agree to our <a href="#" v-b-toggle.collapse3>use of cookies</a>. 
            </h5>
            <b-collapse id="collapse3">
              <b-card>
                This site, like many others, uses small files called cookies to help us customise your experience. 
                For example, when you change the filter settings, or login to Steemconnect, we keep track using files 
                such as cookies. Using this site signifies your acceptance of our use of cookies.
              </b-card>
            </b-collapse>
            </b-alert>
            <header-bar></header-bar>
            <keep-alive include="homepage">
                <router-view></router-view>
            </keep-alive>
        </div>
        `
}).$mount('#app');
