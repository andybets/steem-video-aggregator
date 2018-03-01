<template>
  <div>

    <span v-if="showVotesPanel">
      <span :id="'popoverPayout-sync-' + author + permlink" v-text="payout_string" class="action-link" style="cursor:pointer;"></span>
      <b-popover :show.sync="show_vote_contributions" :target="'popoverPayout-sync-' + author + permlink" title="Vote Contributions">
        <div style="width:200px;height:1px"></div> 
        <b-container v-if="show_vote_contributions" class="px-0 mx-0" v-click-outside="closeVoteContributions">
          <b-row no-gutters>
            <b-col cols="12" >
              <b-container style="border-bottom:1px solid #EEEEEE;" class="px-0 mx-0" v-for="c in vote_contributions" :key="c.voter">
                <b-row no-gutters>
                  <b-col cols="7">
                    <a style="font-weight:800" v-if="c.voter==$globals.username" v-text="c.voter" :href="'https://steemit.com/@' + c.voter" target="_blank"></a>
                    <a v-else v-text="c.voter" :href="'https://steemit.com/@' + c.voter" target="_blank"></a>
                  </b-col>
                  <b-col cols="5" style="text-align:right">
                    <span v-html="c.contribution"></span>
                  </b-col>
                </b-row>
              </b-container>
            </b-col>
          </b-row>
        </b-container>
      </b-popover>

      &nbsp;&nbsp;

        <icon style="vertical-align:middle" v-if="up_voting" :color="'green'" name="spinner" scale="1" spin></icon>
        <icon style="vertical-align:middle" :id="'popoverUpVote-sync-' + author + permlink" v-else :color="up_vote_hover||up_voted ? 'green' : 'grey'" name="arrow-circle-up" scale="1.3" @mouseover.native="up_vote_hover=true"  @mouseleave.native="up_vote_hover=false" @click.native="checkUpVote"></icon>
        <b-popover :show.sync="show_up_vote_slider" :target="'popoverUpVote-sync-' + author + permlink">
          <div style="width:300px;height:1px"></div>
          <b-container v-if="show_up_vote_slider" v-click-outside="closeVoteSliders">
            <b-row no-gutters>
              <b-col cols="12">
                <vue-slider ref="up_vote_slider" v-model="vote_percent"></vue-slider>
              </b-col>
            </b-row>
          </b-container>
        </b-popover>

        <icon style="vertical-align:middle" v-if="down_voting" :color="'red'" name="spinner" scale="1" spin></icon>
        <icon style="vertical-align:middle" :id="'popoverDownVote-sync-' + author + permlink" v-else :color="down_vote_hover||down_voted ? 'red' : 'grey'" name="arrow-circle-down" scale="1.3" @mouseover.native="down_vote_hover=true"  @mouseleave.native="down_vote_hover=false"  @click.native="checkDownVote"></icon>
        <b-popover :show.sync="show_down_vote_slider" :target="'popoverDownVote-sync-' + author + permlink">
          <div style="width:300px;height:1px"></div> 
          <b-container v-if="show_down_vote_slider" v-click-outside="closeVoteSliders">
            <b-row no-gutters>
              <b-col cols="12">
                <vue-slider ref="down_vote_slider" v-model="vote_percent"></vue-slider>
              </b-col>
            </b-row>
          </b-container>
        </b-popover>

      &nbsp;&nbsp;
    </span>

    <span class="action-link" style="vertical-align:middle" @click="is_comment_input_panel_open=!is_comment_input_panel_open" v-show="!is_comment_input_panel_open" v-text="'Reply'"></span>

    <div v-show="is_comment_input_panel_open">
      <b-container fluid class="commentinteractionspanel">
        <b-row>
          <b-col>

            <b-container class="py-0 px-0">
              <b-row no-gutters>
                <b-col cols="auto flex-nowrap">
                  <b-img onerror="this.src='https://steemitimages.com/u/avatarblank/avatar/small'" :src="'https://steemitimages.com/u/' + $globals.username + '/avatar/small'" rounded="circle" blank-color="#777" style="width:40px;height:40px"/>
                </b-col>
                <b-col cols="">
                  <b-container fluid>
                    <b-row class="py-1">
                      <b-col>
                        <b-form-textarea id="commenttextarea"
                          v-model="text"
                          placeholder="Add a public comment..."
                          :rows="1"
                          :max-rows="5" 
                          :disabled="is_comment_input_panel_disabled" 
                          @focus.native="onFocus" 
                          @blur.native="onBlur">
                        </b-form-textarea>
                      </b-col>
                    </b-row>
                    <b-row class="py-1">
                      <b-col>
                        <div class="float-right">
                          <b-button variant="link" :disabled="is_comment_input_panel_disabled" @click="is_comment_input_panel_open=false">Cancel</b-button>
                          <b-button variant="success" :disabled="is_comment_input_panel_disabled" @click="submitComment">Comment</b-button>
                        </div>
                      </b-col>
                    </b-row>
                  </b-container>
                </b-col>
              </b-row>
            </b-container>

          </b-col>
        </b-row>
      </b-container>
    </div>
  </div>
</template>

<script>
  import { bus } from './main.js'
  export default {
    name: 'commentinteractionspanel',
    props: ['author', 'permlink', 'openCommentInputPanel', 'showVotesPanel', 'payoutString', 'upVoted', 'downVoted'],
    mounted: function() {
    },
    methods: {
      onFocus: function() {
        window.removeEventListener('keydown', window.video_key_listener);
      },
      onBlur: function() {
        window.addEventListener('keydown', window.video_key_listener);
      },
      submitComment: function() {
        var new_permlink = this.permlink + '-' + Date.now();
//        var jsonMetadata = { "tags": ["steem"], "app":"multi.tube/0.4" };
        var jsonMetadata = { app:"multi.tube/0.4" };
        var success_callback = this.submittedComment;
        var error_callback = this.submitCommentError;
        this.is_comment_input_panel_disabled = true;
        this.$globals.comment(this.author, this.permlink, this.$globals.username, new_permlink, '', this.text, jsonMetadata, success_callback, error_callback)
      },
      submittedComment: function() {
        // update parent
        this.is_comment_input_panel_disabled = false;
        this.is_comment_input_panel_open = false;
        this.text = '';
        this.$emit('submittedComment');
      },
      submitCommentError: function() {
        // show comment post failed
        this.is_comment_input_panel_disabled = false;
        alert('Sorry, your comment was not saved. Please try again.');
      },

      checkUpVote: function() {
        if (this.show_up_vote_slider) {
          var cmp = this
          if (this.vote_percent > 0) { this.up_voting = true; }
          this.$globals.vote(this.author, this.permlink, parseInt(this.vote_percent*100), function() {
              cmp.$globals.getVotesInfo(cmp.author, cmp.permlink, cmp.displayVoteInfo, null);
          }, function() {
              cmp.$globals.getVotesInfo(cmp.author, cmp.permlink, cmp.displayVoteInfo, null);
          });
        }
      },
      checkDownVote: function() {
        if (this.show_down_vote_slider) {
          var cmp = this
          if (this.vote_percent > 0) { this.down_voting = true; }
          this.$globals.vote(this.author, this.permlink, -parseInt(this.vote_percent*100), function() {
              cmp.$globals.getVotesInfo(cmp.author, cmp.permlink, cmp.displayVoteInfo, null);
          }, function() {
              cmp.$globals.getVotesInfo(cmp.author, cmp.permlink, cmp.displayVoteInfo, null);
          });
        }
      },

      displayVoteInfo: function(total_payout, up_voted, down_voted, vote_contributions) {
        this.up_voting = false;
        this.down_voting = false;
        this.up_voted = up_voted;
        this.down_voted = down_voted;
        this.payout_string = '$' + total_payout.toFixed(3);
        this.vote_contributions = vote_contributions;
        this.$globals.default_vote_percent = this.vote_percent;
      },

      closeVoteSliders: function() {
        this.show_up_vote_slider = false;
        this.show_down_vote_slider = false;
      },
      closeVoteContributions: function() {
        this.show_vote_contributions = false;
      }


    },
    watch: {
      payoutString: function(val) {
        this.payout_string = val;
      },
      upVoted: function(val) {
        this.up_voted = val;
      },
      downVoted: function(val) {
        this.down_voted = val;
      },
      show_vote_contributions: function(val) {
        this.$globals.getVotesInfo(this.author, this.permlink, this.displayVoteInfo, null);
      }
    },
    data () {
      return {
        text: '',
        is_comment_input_panel_open: this.openCommentInputPanel,
        is_comment_input_panel_disabled: false,

        vote_percent: this.$globals.default_vote_percent,
        up_vote_hover: false,
        down_vote_hover: false,
        show_up_vote_slider: false,
        show_down_vote_slider: false,
        up_voting: false,
        down_voting: false,
        up_voted: this.upVoted,
        down_voted: this.downVoted,

        payout_string: this.payoutString,

        show_vote_contributions: false,
        vote_contributions: []
    }
  }
}

</script>

<style scoped>
  .commentinteractionspanel {
    padding: 0em;
    padding-top: 0.7em;
    padding-bottom: 0.05em;
    border: none;
  }
</style>