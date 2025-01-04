import {Menu} from "antd"
import {useStyles} from "./styles"
import clsx from "clsx"
import {PlaygroundVariantHistoryProps} from "./types"
import PlaygroundVariantHistoryHeader from "./assets/PlaygroundVariantHistoryHeader"
import PlaygroundPromptToolsConfig from "../PlaygroundPromptToolsConfig"
import PlaygroundVariantConfigPrompt from "../PlaygroundVariantConfigPrompt"
import usePlayground from "../../hooks/usePlayground"
import {variantToPromptsSelector} from "../PlaygroundVariantConfig/assets/helpers"

const PlaygroundVariantHistory: React.FC<PlaygroundVariantHistoryProps> = ({variantId}) => {
    const {prompts = []} = usePlayground({
        variantId,
        hookId: "PlaygroundVariantHistory",
        variantSelector: (variant) => ({
            ...variantToPromptsSelector(variant),
            variantName: variant?.variantName,
        }),
    })
    const classes = useStyles()
    const lintOfRevisions = ["2", "3", "5", "6", "7"]
    const slectedRevision = "5"

    return (
        <>
            <PlaygroundVariantHistoryHeader slectedRevision={slectedRevision} />

            <section className="h-[94%] flex justify-between gap-2">
                <div className={clsx("pt-4 pl-2", classes.menuContainer)}>
                    <Menu
                        items={lintOfRevisions.map((revision) => ({
                            key: revision,
                            label: revision,
                        }))}
                        defaultSelectedKeys={[slectedRevision]}
                        className={clsx("w-[180px]", classes.menu)}
                    />
                </div>

                <main className="w-full p-1 pr-4">
                    {prompts.map((prompt, promptIndex) => (
                        <PlaygroundVariantConfigPrompt
                            key={prompt.key as string}
                            promptIndex={promptIndex}
                            variantId={variantId}
                        />
                    ))}

                    <PlaygroundPromptToolsConfig />
                </main>
            </section>
        </>
    )
}

export default PlaygroundVariantHistory
