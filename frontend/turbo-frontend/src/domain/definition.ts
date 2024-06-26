import { RJSFSchema } from "@rjsf/utils";

export interface Definition {
  name: string;
  description: string | null;
  run_function: string;
  wait_time: number;
  single_run: boolean;
  meta: {
    created_by: string;
  };
  tuple_result_is_single_value: boolean;
  parameters: {
    queues: {
      input_queue: {
        description: string | null;
      };
      extra_queues: {
        quantity: number;
        description: string | null;
      };
      output_queues: {
        quantity: number;
        description: string | null;
      };
    };
    fields: RJSFSchema | null;
  };
}
