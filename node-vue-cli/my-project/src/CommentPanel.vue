<template>
  <div>
      <b-container fluid class="commentpanel">

        <!-- if top level, body and some interactions parts are handled by playpage, so don't include again //-->
        <b-row v-if="topLevel">
          <b-col>
            <comment-interactions-panel :author="author" :permlink="permlink" :showVotesPanel="false" :openCommentInputPanel="true" @submittedComment="updateReplies" @startCommentEditing="startCommentEditing"></comment-interactions-panel>
          </b-col>
        </b-row>
        <b-row v-if="topLevel" v-for="comment in replies" :key="comment.permlink">
          <b-col>
            <comment-panel :category="comment.category" :author="comment.author" :permlink="comment.permlink" :replyCount="comment.reply_count" :body="comment.body" :initialPayoutString="comment.payout_string" :ageString="comment.age_string" :initialUpVoted="comment.up_voted" :initialDownVoted="comment.down_voted" :load="false"></comment-panel>
          </b-col>
        </b-row>

        <!-- if not top level, show avatar and body as well as other stuff //-->
        <b-row v-if="!topLevel">
          <b-col>
            <b-container class="py-2 px-0">
              <b-row no-gutters>
                <b-col cols="auto flex-nowrap">
                  <b-img-lazy onerror="this.src='https://steemitimages.com/u/avatarblank/avatar/small'" :src="'https://steemitimages.com/u/' + author + '/avatar/small'" rounded="circle" blank-color="#777" style="width:40px;height:40px"/>
                </b-col>
                <b-col cols="">
                  <b-container fluid>
                    <b-row>
                      <b-col>
                        <a :href="'https://steemit.com/@' + author"><b v-text="author"></b></a> - {{ ageString }}
                      </b-col>
                    </b-row>
                    <b-row>
                      <b-col>

                        <b-container fluid v-if="comment_edit_mode">
                          <b-row class="py-1">
                            <b-col>
                              <b-form-textarea 
                                v-model="comment_body" 
                                :rows="1" 
                                :max-rows="5" 
                                :disabled="is_comment_editor_disabled" >
                              </b-form-textarea>
                            </b-col>
                          </b-row>
                          <b-row class="py-1">
                            <b-col>
                              <div class="float-right">
                                <b-button variant="link" :disabled="is_comment_editor_disabled" @click="cancelCommentEditing">Cancel</b-button>
                                <b-button variant="success" :disabled="is_comment_editor_disabled" @click="updateComment">Save</b-button>
                              </div>
                            </b-col>
                          </b-row>
                        </b-container>

                        <div v-else v-html="comment_body"></div>

                      </b-col>
                    </b-row>

                    <b-row>
                      <b-col>
                        <comment-interactions-panel :author="author" :permlink="permlink" :showVotesPanel="true" :openCommentInputPanel="false" :payoutString="initialPayoutString" :upVoted="initialUpVoted" :downVoted="initialDownVoted" @submittedComment="updateReplies" @startCommentEditing="startCommentEditing"></comment-interactions-panel>
                      </b-col>
                    </b-row>

                    <b-row v-show="(!loaded_replies) && replyCount>0">
                      <b-col>
                        <div class="action-link" @click="fetchData" v-text="'Show Replies'"></div>
                      </b-col>
                    </b-row>

                    <b-row v-show="loaded_replies" v-for="comment in replies" :key="comment.permlink">
                      <b-col>
                        <comment-panel :category="comment.category" :author="comment.author" :permlink="comment.permlink" :replyCount="comment.reply_count" :body="comment.body" :initialPayoutString="comment.payout_string" :ageString="comment.age_string" :initialUpVoted="comment.up_voted" :initialDownVoted="comment.down_voted" :load="false"></comment-panel>
                        
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
</template>

<script>
  import { bus } from './main.js'
  export default {
    name: 'commentpanel',
    props: ['topLevel', 'category', 'author', 'permlink', 'replyCount', 'load', 'body', 'ageString', 'initialPayoutString', 
            'initialUpVoted', 'initialDownVoted'],
    mounted: function() {
      if (this.load) {
        setTimeout(this.fetchData, 500);
      }
    },
    methods: {
      fetchData: function() {
        console.log('/f/api/state/' + this.category + '/@' + this.author + '/' + this.permlink);
        this.$http.get('/f/api/state/' + this.category + '/@' + this.author + '/' + this.permlink)
         .then(response => {
            function compare(a,b) {
              if (a.created > b.created)
                return -1;
              if (a.created < b.created)
                return 1;
              return 0;
            }
            var replies = response.data.replies;
            if (this.$globals.loggedIn) {
              for (var i = 0; i < replies.length; i++) {
                for (var j = 0; j < replies[i].active_votes.length; j++) {
                  if (this.$globals.username == replies[i].active_votes[j].voter) {
                    if (replies[i].active_votes[j].percent > 0) {
                        replies[i]['up_voted'] = true;
                        break;
                    }
                    if (replies[i].active_votes[j].percent < 0) {
                        replies[i]['down_voted'] = true;
                        break;
                    }                  
                  }
                }
              }
            }
            replies.sort(compare);
            this.replies = replies;
            this.loaded_replies = true;
            this.payout_string = response.data.payout_string;
        });
      },

      updateReplies: function() {
        this.fetchData();
      },

      startCommentEditing: function() {
        this.comment_edit_mode = true;        
      },
      cancelCommentEditing: function() {
        this.comment_body = this.pre_edit_body;
        this.comment_edit_mode = false;
      },
      updateComment: function() {
//        var jsonMetadata = { "tags": ["steem"], "app":"multi.tube/0.4" };
        var jsonMetadata = { app:"multi.tube/0.4" };
        var success_callback = this.updatedComment;
        var error_callback = this.updateCommentError;
        this.is_comment_editor_disabled = true;
        this.$globals.comment(this.$parent.author, this.$parent.permlink, this.$globals.username, this.permlink, '', this.comment_body, jsonMetadata, false, success_callback, error_callback);
      },
      updatedComment: function() {
        this.is_comment_editor_disabled = false;
        this.comment_edit_mode = false;
      },
      updateCommentError: function(e) {
        this.is_comment_editor_disabled = false;
        alert('Sorry, your comment update was not saved. Please try again. ' + e);
      }

    },
    watch: {
      initialPayoutString: function(val) {
        this.payout_string = val;
      }
    },
    data () {
      return {
        loaded_replies: false,
        replies: [],
        reply_input_open: false,
        payout_string: '',
        comment_body: this.body,
        pre_edit_body: this.body,
        comment_edit_mode: false,
        is_comment_editor_disabled: false
    }
  }
}

</script>

<style scoped>
  .commentpanel {
    padding: 0em;
    padding-top: 0.7em;
    padding-bottom: 0.05em;
    border: none;
  }
</style>