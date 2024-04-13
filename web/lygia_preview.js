import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

const compile_shader = async (shader) => {
    try {
        const res = await api.fetchApi("/shaders/build", {
            method: "POST",
            body: JSON.stringify({
                source: shader,
            }),
        });
        console.log(res);
        const output = await res.json();
        return output;
    } catch (e) {
        console.error(e);
    }
};

app.registerExtension({
    name: "mtb.lygia",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "LygiaProgram") {
        } else if (nodeData.name === "LygiaUniforms") {
            const onc = nodeType.prototype.onNodeCreated;

            nodeType.prototype.onNodeCreated = async function () {
                const r = onc ? onc.apply(this, arguments) : undefined;
                const node = this;
                const compile_button = this.addWidget(
                    "button",
                    "Compile",
                    "compile",
                    function onCompile() {
                        console.log("OK");
                        if (!node.widgets) {
                            console.log(node);
                            return;
                        }
                        const source = node.widgets.find(
                            (w) => w.name === "shader",
                        );
                        if (source) {
                            console.log("Sending shader", source.value);
                            compile_shader(source.value).then((r) => {
                                console.log("COMPILED SHADER", r);
                                app.canvas.setDirty(true);
                                console.log({
                                    widgets: node.widgets,
                                    inputs: node.inputs,
                                    node: node,
                                });
                            });
                        }
                    },
                );
                return r;
            };
        }
    },
});
