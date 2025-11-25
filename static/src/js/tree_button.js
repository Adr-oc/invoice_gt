/** @odoo-module */
import { ListController } from "@web/views/list/list_controller";
import { registry } from '@web/core/registry';
import { listView } from '@web/views/list/list_view';

export class HrTimeListController extends ListController {
   setup() {
       super.setup();
   }
   OnTestClick() {
       this.actionService.doAction({
          type: 'ir.actions.act_window',
          res_model: 'invoice.wizzard.payments',
          name: 'Cargar Pagos',
          view_mode: 'form',
          views: [[false, 'form']],
          target: 'new',
          res_id: false,
          context: { from_test_click: true },  // Agregar contexto específico
      });
   }
   OnNewButtonClick() {
       this.actionService.doAction({
          type: 'ir.actions.act_window',
          res_model: 'invoice.wizzard.payments',  // Usar el mismo modelo
          name: 'Cargar Pago Agrupado',
          view_mode: 'form',
          views: [[false, 'form']],
          target: 'new',
          res_id: false,
          context: { from_new_button_click: true },  // Contexto específico para el botón agrupado
      });
   }
}

registry.category("views").add("button_in_tree", {
   ...listView,
   Controller: HrTimeListController,
   buttonTemplate: "button_time.ListView.Buttons",
});
