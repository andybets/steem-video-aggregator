<template>
  <div class='headerbar' v-click-outside="closeHeaderPanels">
      <b-navbar type="light" variant="light" fixed="top">
        <b-navbar-brand left><b-img class="ml-md-1" width="73px" height="44px" src="/dist/images/home-logo.png" style="padding-top:5px;padding-bottom:0px;cursor:pointer;" v-on:click="closeHeaderPanels();$router.push('/');"/></b-navbar-brand>
        <b-nav-form right>
              <b-container>
                <b-row>
                  <b-col style="padding-right:0px">
                    <a :class="{iconactive: preferences_form_open}" href="#" v-on:click="openPreferences()">
                      <span v-if="$globals.preferences_not_default" style="color:red!important"><icon name="cogs" scale="1.7" style="vertical-align:middle"></icon></span>
                      <span v-else><icon name="cogs" scale="1.5" style="vertical-align:middle"></icon></span>
                      </a>
                    &nbsp;
                    <a :class="{iconactive: filter_form_open}" href="#" v-on:click="openFilter()">
                        <span v-if="$globals.filter_not_default" style="color:red!important"><icon name="filter" scale="1.7" style="vertical-align:middle"></icon></span>
                        <span v-else><icon name="filter" scale="1.5" style="vertical-align:middle"></icon></span>
                    </a>
                    &nbsp;
                    <a :class="{iconactive: search_form_open}"href="#" v-on:click="openSearch()"><icon name="search" scale="1.7" style="vertical-align:middle"></icon></a>
                    &nbsp;
                    <b-button v-if="!$globals.loggedIn" v-on:click="$globals.startLogin" variant="primary" size="sm">Login</b-button>
                    <b-img v-else id="popoverLogout-sync" :src="'https://steemitimages.com/u/' + $globals.username + '/avatar/small'" rounded="circle" blank-color="#777" style="width:32px;height:32px"/>

                    <b-popover :show.sync="show_logout_popover" target="popoverLogout-sync">
                      <div style="width:75px;height:1px"></div>
                      <b-container v-show="show_logout_popover" class="px-0 mx-0" v-click-outside="closeLogoutPopover">
                        <b-row no-gutters>
                          <b-col cols="12">
                            <b-button style="cursor:pointer;" :variant="'link'" :size="'sm'" v-text="'Log Out'" @click="$globals.logout"></b-button>
                          </b-col>
                        </b-row>
                      </b-container>
                    </b-popover>


<!--                    <b-img v-if="$globals.userImageURL" :src="$globals.userImageURL" rounded="circle" width="35" height="35" blank-color="#777" class="mr-1" /> //-->
                  </b-col>
                </b-row>
              </b-container>  
        </b-nav-form>
      </b-navbar>

      <b-collapse :visible="search_form_open" id="searchform" ref="searchform">
        <b-card>
          <div class="input-group">
            <b-form-input @focus.native="$event.target.select()" v-model="$globals.search_terms" v-on:keyup.native.enter="startSearch" ref="searchinput" size="md" type="text" placeholder="Search"/>
            &nbsp;
            <b-button v-on:click="startSearch" size="md" type="submit"><icon name="search"></icon></b-button>
          </div>
        </b-card>
      </b-collapse>

      <b-collapse :visible="filter_form_open" id="filterform" ref="filterform">
        <b-container fluid class="p-3 mx-3" style="padding-bottom:2px!important">
          <b-row>
            <b-col class="pl-2 pl-sm-5 pl-md-2 pl-lg-5" cols="6" md="3">
                <h5>Type</h5>
                <b-form-group>
                  <b-form-checkbox-group v-model="$globals.filter_included_types"
                                      :options='filter_type_options' 
                                      stacked
                                      name="filter_types">
                  </b-form-checkbox-group>
                </b-form-group>
            </b-col>
            <b-col class="pl-2 pl-sm-5 pl-md-2 pl-lg-5" cols="6" md="3">
                <h5>Duration</h5>
                <b-form-group>
                  <b-form-radio-group v-model="$globals.filter_duration_selection"
                                      :options='filter_duration_options' 
                                      stacked
                                      name="filter_duration">
                  </b-form-radio-group>
                </b-form-group>
            </b-col>
            <b-col class="pl-2 pl-sm-5 pl-md-2 pl-lg-5" cols="6" md="3">
                <h5>Age</h5>
                <b-form-group>
                  <b-form-radio-group v-model="$globals.filter_age_selection"
                                      :options='filter_age_options' 
                                      stacked
                                      name="filter_age">
                  </b-form-radio-group>
                </b-form-group>
            </b-col>
            <b-col class="pl-2 pl-sm-5 pl-md-2 pl-lg-5" cols="6" md="3">
                <h5>Sort By</h5>
                <b-form-group>
                  <b-form-radio-group v-model="$globals.filter_sort_selection"
                                      :options='filter_sort_options' 
                                      stacked
                                      name="filter_sort">
                  </b-form-radio-group>
                </b-form-group>
            </b-col>
          </b-row>
        </b-container>
      </b-collapse>

      <b-collapse :visible="preferences_form_open" id="preferencesform" ref="preferencesform">
        <b-container fluid class="p-3 mx-3" style="padding-bottom:2px!important">
          <b-row>
            <b-col class="pl-2 pl-sm-5 pl-md-2 pl-lg-5">
                <h5>Exclude...</h5>
                <b-form-checkbox id="exclude_nsfw"
                                 v-model="$globals.filter_exclude_nsfw"
                                 value="true"
                                 unchecked-value="false">
                  Videos marked as NSFW (not suitable for work).
                </b-form-checkbox><br>
                <b-form-checkbox id="exclude_old_video"
                                 v-model="$globals.filter_exclude_old_video"
                                 value="true"
                                 unchecked-value="false">
                  Videos uploaded more than 7 days before the post.
                </b-form-checkbox><br>

                <label for="excluded_authors">Videos which were not posted by any of these accounts</label>
                <input-tag id="excluded_authors"
                           :tags.sync="$globals.filter_excluded_authors"
                           placeholder="press enter between account names">
                </input-tag>
                <div style="height:10px"></div>
                <label for="excluded_voters">Videos which were voted for by any of these accounts</label>
                <input-tag id="excluded_voters"
                           :tags.sync="$globals.filter_excluded_voters"
                           placeholder="press enter between account names">
                </input-tag>

                <br>

                <h5>Include only...</h5>

                <label for="included_authors">Videos which were posted by any of these accounts</label>
                <input-tag id="included_authors"
                           :tags.sync="$globals.filter_included_authors"
                           placeholder="press enter between account names">
                </input-tag>
                <div style="height:10px"></div>
                <label for="included_voters">Videos which were voted for by any of these accounts</label>
                <input-tag id="included_voters"
                           :tags.sync="$globals.filter_included_voters"
                           placeholder="press enter between account names">
                </input-tag>

                <br>

<!--
                <h5>Options</h5>
                <b-form-checkbox disabled id="reputation_filter_active"
                                 v-model="$globals.filter_reputation_active"
                                 value="true"
                                 unchecked-value="false">
                  Include only posts where author reputation is between [..] and [..]
                </b-form-checkbox><br>
                <b-form-checkbox disabled id="quick_play_enabled"
                                 v-model="$globals.filter_quick_play_enabled"
                                 value="true"
                                 unchecked-value="false">
                  Clicking thumbnails plays video in place.
                </b-form-checkbox><br>
//-->                

                <!-- todo - add exclusions filter for authors/tags //-->

            </b-col>
          </b-row>
        </b-container>
      </b-collapse>

  </div>
</template>

<script>
import { bus } from './main.js';
export default {
  name: 'headerbar',
  data () {
    return {
      show_logout_popover: false,
      search_form_open: false,
      filter_form_open: false,
      preferences_form_open: false,
      search_terms: '',
      filter_age_options: [
          {text: 'All', value: 'all'},
          {text: 'Last Hour', value: 'hour'},
          {text: 'Today', value: 'today'},
          {text: 'This Week', value: 'week'},
          {text: 'This Month', value: 'month'}
      ],
      filter_type_options: [
          {text: 'YouTube', value: 'youtube'},
          {text: 'DTube', value: 'dtube'},
          {text: 'DLive', value: 'dlive'}
      ],
      filter_duration_options: [
          {text: 'All', value: 'all'},
          {text: 'Short', value: 'short'},
          {text: 'Long', value: 'long'}
      ],
      filter_sort_options: [
          {text: 'Date', value: 'date'},
          {text: 'Payout', value: 'payout'},
          {text: 'Trending', value: 'trending'},
          {text: 'Hot', value: 'hot'}
      ],

    }
  },
  methods: {
    openSearch: function() {
      this.search_form_open = !this.search_form_open;
      this.filter_form_open = false;
      this.preferences_form_open = false;
      // todo - in ios, search box doesn't get focus and load keyboard, fix that
      this.$refs.searchinput.focus();
      setTimeout(this.$refs.searchinput.focus, 100);
    },
    startSearch: function() {
      document.activeElement.blur();
      this.$router.replace('/search/' + this.$globals.search_terms);
      this.search_form_open = false;
    },
    openFilter: function() {
      this.filter_form_open = !this.filter_form_open;
      this.search_form_open = false;
      this.preferences_form_open = false;
    },
    closeHeaderPanels: function() {
      this.search_form_open = false;
      this.filter_form_open = false;
      this.preferences_form_open = false;
    },
    openPreferences: function() {
      this.preferences_form_open = !this.preferences_form_open;
      this.filter_form_open = false;
      this.search_form_open = false;
    },
    closeLogoutPopover: function() {
      this.show_logout_popover = false;
    }
  },
  created() {
    if (this.$route.query.access_token) {
      this.$globals.completeLogin(this.$route.query.access_token);
    }
    window.addEventListener('wheel', this.closeHeaderPanels);
  },
  destroyed() {
    window.removeEventListener('wheel', this.closeHeaderPanels);
  }
}
</script>

<style>

h1, h2 {
  font-weight: normal;
}

h2 {
  margin:0px;
}

h4 {
  font-size: 1.1rem!important;
}
@media (min-width: 576px) {
  h4 {
    font-size: 1.4rem!important;
  }
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 10px;
}

a {
  color: #42b983;
}

.navbar {
  background-color: white!important;
  padding-top:0px;
  padding-bottom: 0px;
  border-bottom: 1px solid #EAEAEA;
}
.headerbar {
  border-bottom: 1px solid lightgrey;
  margin-bottom: 15px;
  background: white;
}

body {
  padding-top: 55px;
  overflow-wrap: break-word;
  word-wrap: break-word;
}

.iconactive {
  border-bottom:2px solid black;
  padding-bottom:10px;
}
.iconmodified {
  color:green!important;
}

.vue-input-tag-wrapper .input-tag {
    background-color: #007bff!important;
    border-radius: 2px;
    border: 1px solid #007bff!important;
    color: #fff!important;
}
.vue-input-tag-wrapper .input-tag .remove:before {
  color:white!important;
}
.vue-input-tag-wrapper .new-tag {
  width: 250px!important;
}
.vue-input-tag-wrapper {
  margin-right: 40px!important;
}

</style>
