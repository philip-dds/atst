import 'svg-innerhtml'
import 'babel-polyfill'
import ally from 'ally.js'

import classes from '../styles/atat.scss'
import Vue from 'vue/dist/vue'
import VTooltip from 'v-tooltip'
import stickybits from 'stickybits'

import dodlogin from './components/dodlogin'
import levelofwarrant from './components/levelofwarrant'
import optionsinput from './components/options_input'
import multicheckboxinput from './components/multi_checkbox_input'
import textinput from './components/text_input'
import checkboxinput from './components/checkbox_input'
import nestedcheckboxinput from './components/nested_checkbox_input'
import EditOfficerForm from './components/forms/edit_officer_form'
import poc from './components/forms/poc'
import oversight from './components/forms/oversight'
import toggler from './components/toggler'
import NewApplication from './components/forms/new_application'
import { EditEnvironmentRole } from './components/forms/edit_environment_role'
import EditApplicationRoles from './components/forms/edit_application_roles'
import MultiStepModalForm from './components/forms/multi_step_modal_form'
import funding from './components/forms/funding'
import uploadinput from './components/upload_input'
import Modal from './mixins/modal'
import selector from './components/selector'
import BudgetChart from './components/charts/budget_chart'
import SpendTable from './components/tables/spend_table'
import EnvironmentsTable from './components/tables/application_environments'
import TaskOrderList from './components/tables/task_order_list.js'
import LocalDatetime from './components/local_datetime'
import ConfirmationPopover from './components/confirmation_popover'
import { isNotInVerticalViewport } from './lib/viewport'
import DateSelector from './components/date_selector'
import SidenavToggler from './components/sidenav_toggler'
import BaseForm from './components/forms/base_form'
import SubmitConfirmation from './components/submit_confirmation'
import DeleteConfirmation from './components/delete_confirmation'
import NewEnvironment from './components/forms/new_environment'
import EnvironmentRole from './components/environment_role'
import SemiCollapsibleText from './components/semi_collapsible_text'
import ToForm from './components/forms/to_form'
import ClinFields from './components/clin_fields'

Vue.config.productionTip = false

Vue.use(VTooltip)

Vue.mixin(Modal)

const app = new Vue({
  el: '#app-root',
  components: {
    dodlogin,
    toggler,
    levelofwarrant,
    optionsinput,
    multicheckboxinput,
    textinput,
    checkboxinput,
    poc,
    oversight,
    NewApplication,
    selector,
    BudgetChart,
    SpendTable,
    EnvironmentsTable,
    TaskOrderList,
    LocalDatetime,
    EditEnvironmentRole,
    EditApplicationRoles,
    MultiStepModalForm,
    ConfirmationPopover,
    funding,
    uploadinput,
    DateSelector,
    EditOfficerForm,
    SidenavToggler,
    BaseForm,
    DeleteConfirmation,
    SubmitConfirmation,
    nestedcheckboxinput,
    NewEnvironment,
    EnvironmentRole,
    SemiCollapsibleText,
    ToForm,
    ClinFields,
  },

  mounted: function() {
    this.$on('modalOpen', data => {
      if (data['isOpen']) {
        document.body.className += ' modal-open'
        this.activeModal = data['name']

        var handler = ally.maintain.disabled({
          filter: `#${this.modalId}`,
        })

        this.allyHandler = handler
      } else {
        this.activeModal = null
        if (this.allyHandler) {
          this.allyHandler.disengage()
          this.allyHandler = null
        }
        document.body.className = document.body.className.replace(
          ' modal-open',
          ''
        )
      }
    })

    const modalOpen = document.querySelector('#modalOpen')

    if (modalOpen) {
      const modal = modalOpen.getAttribute('data-modal')
      this.openModal(modal)
    }

    ally.query.focusable().forEach(function(el) {
      el.addEventListener('focus', function() {
        if (isNotInVerticalViewport(el)) {
          el.scrollIntoView({ block: 'center' })
        }
      })
    })
  },
  delimiters: ['!{', '}'],

  directives: {
    sticky: {
      inserted: el => {
        stickybits(el)
      },
    },
  },
})
