import Vue from 'vue'
import BootstrapVue from "bootstrap-vue"
import VueRouter from 'vue-router'
import vueResource from 'vue-resource'
import HomePage from './HomePage.vue'
import PlayPage from './PlayPage.vue'
import SearchResultsListPage from './SearchResultsListPage.vue'
import ThumbnailsPage from './ThumbnailsPage.vue'
import HeaderBar from './HeaderBar.vue'
import PlayerYoutube from './PlayerYoutube.vue'
import PlayerDtube from './PlayerDtube.vue'
import PlayerDlive from './PlayerDlive.vue'
import CommentPanel from './CommentPanel.vue'
import CommentInteractionsPanel from './CommentInteractionsPanel.vue'
import VideoOverlayPanel from './VideoOverlayPanel.vue'

import "bootstrap/dist/css/bootstrap.min.css"
import "bootstrap-vue/dist/bootstrap-vue.css"

import VueCarousel from 'vue-carousel';
import InfiniteLoading from 'vue-infinite-loading';
import vueSlider from 'vue-slider-component';
import Trend from 'vuetrend';
import InputTag from 'vue-input-tag';

Vue.use(BootstrapVue);
Vue.use(vueResource);
Vue.use(VueRouter);
Vue.use(VueCarousel);
Vue.use(Trend);

Vue.component('vue-slider', vueSlider);
Vue.component('input-tag', InputTag);

var Icon = require('vue-awesome');
Vue.component('icon', Icon);
Vue.component('infinite-loading', InfiniteLoading);

Vue.component('player-youtube', PlayerYoutube);
Vue.component('player-dtube', PlayerDtube);
Vue.component('player-dlive', PlayerDlive);
Vue.component('comment-panel', CommentPanel);
Vue.component('comment-interactions-panel', CommentInteractionsPanel);
Vue.component('video-overlay-panel', VideoOverlayPanel);

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

            // todo - save to, and load this from local storage
            default_vote_percent: 50,

            search_terms: '',
            filter_age_selection: 'all',
            filter_included_types: ['youtube', 'dtube'],
            filter_duration_selection: 'all',
            filter_sort_selection: 'date',            

            filter_exclude_old_video: 'true',
            filter_exclude_nsfw: 'true',
            filter_excluded_voters: [],
            filter_included_voters: [],
            filter_excluded_authors: [],
            filter_included_authors: [],
            filter_excluded_tags: [],
            filter_included_tags: [],
            filter_reputation_active: 'false',
            filter_quick_play_enabled: 'false',

            filter_not_default: false,
            preferences_not_default: false

        }
    },
    watch: {
        filter_age_selection: function() { this.saveFilterValues() },
        filter_included_types: function() { this.saveFilterValues() },
        filter_duration_selection: function() { this.saveFilterValues() },
        filter_sort_selection: function() { this.saveFilterValues() },
        filter_exclude_old_video: function() { this.saveFilterValues() },
        filter_exclude_nsfw: function() { this.saveFilterValues() },
        filter_excluded_voters: function() { this.saveFilterValues() },
        filter_included_voters: function() { this.saveFilterValues() },
        filter_excluded_authors: function() { this.saveFilterValues() },
        filter_included_authors: function() { this.saveFilterValues() },
        filter_excluded_tags: function() { this.saveFilterValues() },
        filter_included_tags: function() { this.saveFilterValues() },
        filter_reputation_active: function() { this.saveFilterValues() },
        filter_quick_play_enabled: function() { this.saveFilterValues() }
    },
    created: function() {
        // try and load filters/preferences from local storage
        try {
            this.loadFilterValues();
        } catch (e) {
            console.log('Incompatible filter settings. May not have fully loaded them.')
        }

        steem.api.setOptions({ url: 'https://api.steemit.com' });

        // set appropriate SteemConnect callbackURL for local testing of production
        var callbackURL = '';
        if (window.location.hostname == 'localhost') {
            callbackURL = window.location.protocol + '//' + window.location.hostname + ':' + window.location.port + '/'
        } else {
            callbackURL = window.location.protocol + '//' + window.location.hostname + '/'
        }

        sc2.init({
          baseURL: 'https://v2.steemconnect.com',
          app: 'multitube.app',
          callbackURL: callbackURL,
          scope: ['vote', 'comment', 'delete_comment', 'comment_options', 'custom_json']
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
                    if (window.location.search.indexOf('token=') >= 0) {
                        router.replace(window.location.pathname);
                    }
//                    console.log(user);
//                    console.log(metadata);
                } else {
                    t.loggedIn = false;
                    localStorage.clear();
                    console.log(err);
                }
              });
        },
        logout: function() {
            this.loggedIn = false;
            this.username = null;
            this.token = null;
            this.userImageURL = null;
            localStorage.removeItem("username");
            localStorage.removeItem("token");
            localStorage.removeItem("userImageURL");
            window.location.reload();
        },
        vote: function(author, permlink, percent, success_callback, error_callback) {
            if (!this.loggedIn) {
                window.alert('Please login to vote.')
                error_callback();
                return;
            }
            sc2.vote(this.username, author, permlink, percent, function (err, res) {
                console.log(err, res);
                if (!err) {
                    success_callback();
                } else {
                    error_callback(err);
                }
            });
        },

        comment: function(parentAuthor, parentPermlink, author, permlink, title, body, jsonMetadata, send_comment_options, success_callback, error_callback) {
            const operations = [];

            const commentOp = [
                'comment',
                {
                  parent_author: parentAuthor,
                  parent_permlink: parentPermlink,
                  author,
                  permlink,
                  title,
                  body,
                  json_metadata: JSON.stringify(jsonMetadata),
                },
            ];
            operations.push(commentOp);

            const commentOptionsConfig = {
                author,
                permlink,
                allow_votes: true,
                allow_curation_rewards: true,
                extensions,
            };

            const extensions = [[0, {
              beneficiaries: [
                {
                  account: 'multi.tube',
                  weight: 2500
                }
              ]
            }]];

            if (send_comment_options && extensions) {
                commentOptionsConfig.extensions = extensions;
                commentOptionsConfig.percent_steem_dollars = 10000;
                commentOptionsConfig.max_accepted_payout = '1000000.000 SBD';
                operations.push(['comment_options', commentOptionsConfig]);
            }

            console.log("OPERATIONS", operations)

            if (true) {
                sc2.broadcast(operations, function (err, res) {
                    console.log(err, res)
                    if (!err) {
                        success_callback();
                    } else {
                        error_callback(err);
                    }
                    if (commentOp) console.log("ORIGINAL COMMENT OBJECT: ", commentOp);
                });
            }
        },

        getVotesInfo: function(authur, permlink, success_callback, error_callback) {
            var cmp = this;
            steem.api.getContent(authur, permlink, function(err, result) {
                if (!err) {
                    var total_payout = parseFloat(result.pending_payout_value) + parseFloat(result.total_payout_value);
                    var votes = result.active_votes;
                    votes = votes.sort(function(a, b) { return Math.abs(parseInt(b.rshares)) - Math.abs(parseInt(a.rshares)) })
                    var total_rshares = 0
                    var up_voted = false;
                    var down_voted = false;
                    for (var i=0; i<votes.length; i++) {
                        if (votes[i].voter == cmp.username && votes[i].percent > 0 ) { up_voted = true; }
                        if (votes[i].voter == cmp.username && votes[i].percent < 0 ) { down_voted = true; }
                        total_rshares = total_rshares + parseInt(votes[i].rshares);
                    }
                    var vote_contributions = votes.map(function(x) {
                        var c =  total_payout * (parseInt(x.rshares) / total_rshares);
                        if (c > 0) {
                            return { voter: x.voter, contribution: '<span style="color:green">' + c.toFixed(3) + '</span>' }
                        } else if (c < 0) {
                            return { voter: x.voter, contribution: '<span style="color:red"> ' + c.toFixed(3) + '</span>' }
                        } else if (c == 0) {
                            return { voter: x.voter, contribution: '<span style="color:grey"> ' + c.toFixed(3) + '</span>' }
                        }
                    });
                    if (vote_contributions.length > 30) {
                        vote_contributions = vote_contributions.slice(0, 30);
                        vote_contributions.push({voter: '(and others)', contribution: ''})
                    }
                    // todo - create sparkline data
                    success_callback(total_payout, up_voted, down_voted, vote_contributions);
                } else {
                    console.log(err);
//                    error_callback(err);
                }
            });
        },

        saveFilterValues: function() {
            // update state of filters for visual indications
            //if ((this.filter_age_selection != 'all') || (this.filter_type_selection != 'all') 
            if ((this.filter_age_selection != 'all') 
                || !(JSON.stringify(this.filter_included_types.slice().sort())==JSON.stringify(['youtube', 'dtube'].sort()) ) 
                || (this.filter_duration_selection != 'all') || (this.filter_sort_selection != 'date') ) {
                this.filter_not_default = true;
            } else {
                this.filter_not_default = false;
            }

            // update state of preferences for visual indications
            if ((this.filter_exclude_old_video != 'true') || (this.filter_exclude_nsfw != 'true') 
                || (this.filter_excluded_voters.length > 0) || (this.filter_included_voters.length > 0)
                || (this.filter_excluded_tags.length > 0) || (this.filter_included_tags.length > 0)
                || (this.filter_excluded_authors.length > 0) || (this.filter_included_authors.length > 0)) {
                this.preferences_not_default = true;
            } else {
                this.preferences_not_default = false;
            }

            localStorage.setItem('filter_age_selection', this.filter_age_selection);
            localStorage.setItem('filter_included_types', JSON.stringify(this.filter_included_types));
            localStorage.setItem('filter_duration_selection', this.filter_duration_selection);
            localStorage.setItem('filter_sort_selection', this.filter_sort_selection);
            localStorage.setItem('filter_exclude_old_video', this.filter_exclude_old_video);
            localStorage.setItem('filter_exclude_nsfw', this.filter_exclude_nsfw);
            localStorage.setItem('filter_excluded_voters', JSON.stringify(this.filter_excluded_voters));
            localStorage.setItem('filter_included_voters', JSON.stringify(this.filter_included_voters));
            localStorage.setItem('filter_excluded_authors', JSON.stringify(this.filter_excluded_authors));
            localStorage.setItem('filter_included_authors', JSON.stringify(this.filter_included_authors));
            localStorage.setItem('filter_excluded_tags', JSON.stringify(this.filter_excluded_tags));
            localStorage.setItem('filter_included_tags', JSON.stringify(this.filter_included_tags));
            localStorage.setItem('filter_reputation_active', this.filter_reputation_active);
            localStorage.setItem('filter_quick_play_enabled', this.filter_quick_play_enabled);
            bus.$emit('filtersChanged'); // todo - prevent this firing several time on initial fetch if it does
        },
        loadFilterValues: function() {
            if (localStorage["filter_exclude_old_video"]) { // all saved when one is, so just need to check one
                this.filter_age_selection = localStorage['filter_age_selection'];
                this.filter_included_types = JSON.parse(localStorage['filter_included_types']);
                this.filter_duration_selection = localStorage['filter_duration_selection'];
                this.filter_sort_selection = localStorage['filter_sort_selection'];
                this.filter_exclude_old_video = localStorage['filter_exclude_old_video'];
                this.filter_exclude_nsfw = localStorage['filter_exclude_nsfw'];
                this.filter_excluded_voters = JSON.parse(localStorage['filter_excluded_voters']);
                this.filter_included_voters = JSON.parse(localStorage['filter_included_voters']);
                this.filter_excluded_authors = JSON.parse(localStorage['filter_excluded_authors']);
                this.filter_included_authors = JSON.parse(localStorage['filter_included_authors']);
                this.filter_excluded_tags = JSON.parse(localStorage['filter_excluded_tags']);
                this.filter_included_tags = JSON.parse(localStorage['filter_included_tags']);
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
        { path: '/@:author/:permlink', component: PlayPage, props: true},

        // results pages
        { path: '/search/:search_terms', component: SearchResultsListPage },
        { path: '/trending', component: ThumbnailsPage, props: { 
            page_title: 'Trending Videos', 
            video_list_url: '/f/api/trending-videos' }},
        { path: '/hot', component: ThumbnailsPage, props: { 
            page_title: 'Hot Videos', 
            video_list_url: '/f/api/hot-videos' }},
        { path: '/new', component: ThumbnailsPage, props: { 
            page_title: 'New Videos', 
            video_list_url: '/f/api/new-videos' }},
        { path: '/@:author', component: ThumbnailsPage, props: { 
            page_title: 'Account Videos', 
            video_list_url: '/f/api/account-videos' }},

        // convenient advanced search urls
        { path: '/advanced-search/:search_terms&tag=:tag&votedby=:votedby', component: SearchResultsListPage, props: true},
        { path: '/advanced-search/:search_terms&votedby=:votedby&tag=:tag', component: SearchResultsListPage, props: true},
        { path: '/advanced-search/:search_terms&tag=:tag', component: SearchResultsListPage, props: true},
        { path: '/advanced-search/:search_terms&votedby=:votedby', component: SearchResultsListPage, props: true}

    ],

    // todo - improve scroll position retention
    scrollBehavior (to, from, savedPosition) {
      if (savedPosition) {
          return new Promise((resolve, reject) => {
                setTimeout(() => {
                  resolve(savedPosition)
                }, 500)
              })
      }
    }

});

new Vue({
  router,
  components: {
    'header-bar': HeaderBar 
  },
  data: function() {
        return {
            showDismissibleAlert: true,
            showMainAlert: false
        }
    },
  methods: {
    hideCookieNotice: function() {
        this.showDismissibleAlert=false;
        localStorage.setItem("cookiesAccepted", 'Yes');
    },
    hideMainNotice: function() {
        this.showMainAlert=false;
    }
  },
  template: `
        <div id="app">
            <b-alert variant="primary" style="margin-bottom:3px" dismissible :show="showMainAlert" @dismissed="hideMainNotice">
            <h5>
            Notice (<a href="#" v-b-toggle.collapsemain>see more info</a>). 
            </h5>
            <b-collapse id="collapsemain">
              <b-card>  
                This is placeholder text for a notice which always appears at the top of the site.
              </b-card>
            </b-collapse>
            </b-alert>

            <b-alert variant="primary" v-if="!$globals.cookiesAccepted" style="margin-bottom:3px" dismissible :show="showDismissibleAlert" @dismissed="hideCookieNotice">
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
            <keep-alive :include='["homepage", "searchresultslistpage", "thumbnailspage"]'>
                <router-view></router-view>
            </keep-alive>
        </div>
        `
}).$mount('#app');
