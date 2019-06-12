import { emitEvent } from '../lib/emitters'
import FormMixin from '../mixins/form'

export default {
  name: 'optionsinput',

  mixins: [FormMixin],

  props: {
    name: String,
    initialErrors: {
      type: Array,
      default: () => [],
    },
    initialValue: String,
    watch: {
      type: Boolean,
      default: false,
    },
    optional: Boolean,
  },

  created: function() {
    emitEvent('field-mount', this, {
      optional: this.optional,
      name: this.name,
    })
  },

  data: function() {
    const showError = (this.initialErrors && this.initialErrors.length) || false
    return {
      showError: showError,
      showValid: !showError && !!this.initialValue,
      validationError: this.initialErrors.join(' '),
      value: this.initialValue,
    }
  },

  methods: {
    onInput: function(e) {
      this.showError = false
      this.showValid = true

      emitEvent('field-change', this, {
        value: e.target.value,
        name: this.name,
        watch: this.watch,
        valid: this.showValid,
      })
    },
  },
}
