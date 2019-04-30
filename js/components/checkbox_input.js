import { emitEvent } from '../lib/emitters'
import nestedcheckboxinput from './nested_checkbox_input'

export default {
  name: 'checkboxinput',

  components: {
    nestedcheckboxinput,
  },

  props: {
    name: String,
    initialChecked: Boolean,
  },

  data: function() {
    return {
      isChecked: this.initialChecked,
    }
  },

  methods: {
    onInput: function(e) {
      emitEvent('field-change', this, {
        value: e.target.checked,
        name: this.name,
      })
    },
  },
}
