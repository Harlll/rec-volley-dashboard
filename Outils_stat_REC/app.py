import streamlit as st
import pandas as pd
import altair as alt
from src.config import APP_TITLE, APP_ICON
from src.ui import apply_global_style
from src.data_loader import save_uploaded_file_temporarily, parse_dvw_file

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
)

apply_global_style()

st.markdown(
    """
    <div class="header-bar">
        <div class="header-title">REC Volley Performance Dashboard</div>
    </div>
    """,
    unsafe_allow_html=True
)

tab_files, tab_graph, tab_analysis = st.tabs(["Fichiers match", "Graphique", "Analyse"])

if "plays_df" not in st.session_state:
    st.session_state.plays_df = None

if "uploaded_match_name" not in st.session_state:
    st.session_state.uploaded_match_name = None

with tab_files:
    uploaded_dvw = st.file_uploader("Déposer un fichier .dvw", type=["dvw"])

    if uploaded_dvw is not None:
        try:
            temp_path = save_uploaded_file_temporarily(uploaded_dvw)
            plays = parse_dvw_file(temp_path)

            st.session_state.plays_df = plays
            st.session_state.uploaded_match_name = uploaded_dvw.name

            st.success(f"Fichier chargé : {uploaded_dvw.name}")
            st.dataframe(plays.head(20), use_container_width=True)
            st.write(plays["video_time"].dropna().head(20).tolist())

        except Exception as e:
            st.error(f"Erreur lecture fichier .dvw : {e}")

with tab_graph:
    df = st.session_state.plays_df

    if df is None or df.empty:
        st.warning("Charge d'abord un fichier .dvw dans l'onglet 'Fichiers match'.")
    else:
        df["video_time_sec"] = pd.to_numeric(df["video_time"], errors="coerce")
        df = df.dropna(subset=["video_time_sec"]).copy()
        df["video_time_sec"] = df["video_time_sec"] - df["video_time_sec"].min()
        df = df.copy()

        score_map = {
            "#": 2,
            "+": 1,
            "!": 0.5,
            "-": -0.5,
            "/": -1,
            "=": -2,
        }

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            team_selected = st.selectbox(
                "Équipe",
                ["Toutes"] + sorted(df["team"].dropna().astype(str).unique().tolist())
            )

        with col2:
            player_selected = st.selectbox(
                "Joueur",
                ["Tous"] + sorted(df["player_name"].dropna().astype(str).unique().tolist())
            )

        with col3:
            action_selected = st.selectbox(
                "Actions",
                ["Toutes"] + sorted(df["skill"].dropna().astype(str).unique().tolist())
            )

        with col4:
            set_selected = st.selectbox(
                "Set",
                ["Tous"] + sorted(df["set_number"].dropna().astype(str).unique().tolist())
            )

        with col5:
            point_phase_selected = st.selectbox(
                "Point phase",
                ["Toutes"] + sorted(df["point_phase"].dropna().astype(str).unique().tolist())
            )

        filtered_df = df.copy()

        if team_selected != "Toutes":
            filtered_df = filtered_df[filtered_df["team"].astype(str) == team_selected]

        if player_selected != "Tous":
            filtered_df = filtered_df[filtered_df["player_name"].astype(str) == player_selected]

        if action_selected != "Toutes":
            filtered_df = filtered_df[filtered_df["skill"].astype(str) == action_selected]

        if set_selected != "Tous":
            filtered_df = filtered_df[filtered_df["set_number"].astype(str) == set_selected]

        if point_phase_selected != "Toutes":
            filtered_df = filtered_df[filtered_df["point_phase"].astype(str) == point_phase_selected]

        filtered_df["evaluation_score"] = filtered_df["evaluation_code"].map(score_map)
        filtered_df = filtered_df.dropna(subset=["evaluation_score"]).copy()

        window_size = st.slider("Fenêtre moyenne glissante", min_value=3, max_value=25, value=8, step=1)

        filtered_df = filtered_df.sort_values(["player_name", "video_time_sec"]).copy()

        filtered_df["performance_smooth"] = (
            filtered_df
            .groupby("player_name")["evaluation_score"]
            .transform(lambda s: s.rolling(window=window_size, min_periods=1).mean())
        )

        chart_df = filtered_df.pivot_table(
            index="video_time_sec",
            columns="player_name",
            values="performance_smooth",
            aggfunc="mean"
        ).sort_index()

        st.markdown("### Performance des joueurs dans le temps")

        if filtered_df.empty:
            st.warning("Aucune donnée exploitable pour ce filtrage.")
        else:
            chart_source = filtered_df[
                ["video_time_sec", "player_name", "performance_smooth", "evaluation_score"]
            ].dropna().copy()

            chart_joueurs = (
                alt.Chart(chart_source)
                .mark_line()
                .encode(
                    x=alt.X(
                        "video_time_sec:Q",
                        title="Temps",
                        axis=alt.Axis(
                            labelExpr="floor(datum.value/60) + ':' + (datum.value%60 < 10 ? '0' : '') + floor(datum.value%60)"
                        )
                    ),
                    y=alt.Y("performance_smooth:Q", title="Performance lissée"),
                    color=alt.Color("player_name:N", title="Joueur")
                )
            )

            trend_source = filtered_df[["video_time_sec", "evaluation_score"]].dropna().copy()

            chart_tendance = (
                alt.Chart(trend_source)
                .transform_regression(
                    "video_time_sec",
                    "evaluation_score"
                )
                .mark_line(
                    color="red",
                    size=3
                )
                .encode(
                    x=alt.X("video_time_sec:Q"),
                    y=alt.Y("evaluation_score:Q")
                )
            )

            chart = (
                chart_joueurs + chart_tendance
            ).properties(height=450)

            st.altair_chart(chart, use_container_width=True)

            

        st.markdown("### Vérification des codes d'évaluation")

        code_check = (
            filtered_df[["evaluation_code", "evaluation_score"]]
            .drop_duplicates()
            .sort_values("evaluation_code")
        )

        st.dataframe(code_check, use_container_width=True)

        st.markdown("### Aperçu des données utilisées")

        st.dataframe(
            filtered_df[
                [
                    "video_time_sec",
                    "player_name",
                    "skill",
                    "evaluation_code",
                    "evaluation_score",
                    "performance_smooth"
                ]
            ].head(30),
            use_container_width=True
        )

with tab_analysis:
    df = st.session_state.plays_df

    if df is None or df.empty:
        st.warning("Charge d'abord un fichier .dvw dans l'onglet 'Fichiers match'.")
    else:
        df_analyse = df.copy()

        score_map = {
            "#": 2,
            "+": 1,
            "!": 0.5,
            "-": -0.5,
            "/": -1,
            "=": -2,
        }

        df_analyse["video_time_sec"] = pd.to_numeric(df_analyse["video_time"], errors="coerce")
        df_analyse = df_analyse.dropna(subset=["video_time_sec", "evaluation_code"]).copy()
        df_analyse["video_time_sec"] = df_analyse["video_time_sec"] - df_analyse["video_time_sec"].min()

        df_analyse["evaluation_score"] = df_analyse["evaluation_code"].map(score_map)
        df_analyse = df_analyse.dropna(subset=["evaluation_score"]).copy()

        if df_analyse.empty:
            st.warning("Aucune donnée exploitable pour l'analyse.")
        else:
            st.markdown("## Analyse temporelle du match")

            taille_bloc_minutes = st.slider(
                "Taille des blocs temporels",
                min_value=1,
                max_value=10,
                value=5,
                step=1
            )

            min_actions_bloc = st.slider(
                "Nombre minimum d'actions par bloc",
                min_value=1,
                max_value=30,
                value=5,
                step=1
            )

            taille_bloc_secondes = taille_bloc_minutes * 60

            df_analyse["bloc_temps"] = (
                df_analyse["video_time_sec"] // taille_bloc_secondes
            ).astype(int)

            analyse_blocs = (
                df_analyse
                .groupby("bloc_temps")
                .agg(
                    temps_debut=("video_time_sec", "min"),
                    temps_fin=("video_time_sec", "max"),
                    evaluation_moyenne=("evaluation_score", "mean"),
                    evaluation_std=("evaluation_score", "std"),
                    nb_actions=("evaluation_score", "count"),

                    set_debut=("set_number", "first"),
                    set_fin=("set_number", "last"),
                    score_home_debut=("home_team_score", "first"),
                    score_home_fin=("home_team_score", "last"),
                    score_away_debut=("visiting_team_score", "first"),
                    score_away_fin=("visiting_team_score", "last"),
                    home_team=("home_team", "first"),
                    visiting_team=("visiting_team", "first"),
                )
                .reset_index()
            )

            analyse_blocs["temps_debut_min"] = analyse_blocs["temps_debut"] / 60
            analyse_blocs["temps_fin_min"] = analyse_blocs["temps_fin"] / 60

            analyse_blocs["periode"] = (
                analyse_blocs["temps_debut_min"].round(1).astype(str)
                + " - "
                + analyse_blocs["temps_fin_min"].round(1).astype(str)
                + " min"
            )
            analyse_blocs["score_debut"] = (
                "Set "
                + analyse_blocs["set_debut"].astype(str)
                + " | "
                + analyse_blocs["score_home_debut"].astype(str)
                + " - "
                + analyse_blocs["score_away_debut"].astype(str)
            )

            analyse_blocs["score_fin"] = (
                "Set "
                + analyse_blocs["set_fin"].astype(str)
                + " | "
                + analyse_blocs["score_home_fin"].astype(str)
                + " - "
                + analyse_blocs["score_away_fin"].astype(str)
            )

            analyse_blocs["score_bloc"] = (
                analyse_blocs["score_debut"]
                + " → "
                + analyse_blocs["score_fin"]
            )

            analyse_blocs_filtre = analyse_blocs[
                analyse_blocs["nb_actions"] >= min_actions_bloc
            ].copy()

            if analyse_blocs_filtre.empty:
                st.warning("Pas assez d'actions pour analyser les blocs temporels avec ce seuil.")
            else:
                meilleur_moment = analyse_blocs_filtre.loc[
                    analyse_blocs_filtre["evaluation_moyenne"].idxmax()
                ]

                pire_moment = analyse_blocs_filtre.loc[
                    analyse_blocs_filtre["evaluation_moyenne"].idxmin()
                ]

                stabilite = analyse_blocs_filtre["evaluation_moyenne"].std()
                amplitude = (
                    analyse_blocs_filtre["evaluation_moyenne"].max()
                    - analyse_blocs_filtre["evaluation_moyenne"].min()
                )

                moyenne_match = df_analyse["evaluation_score"].mean()

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Performance moyenne", f"{moyenne_match:.2f}")

                with col2:
                    st.metric(
                        "Meilleur moment",
                        f"{meilleur_moment['evaluation_moyenne']:.2f}",
                        meilleur_moment["periode"]
                    )

                with col3:
                    st.metric(
                        "Pire moment",
                        f"{pire_moment['evaluation_moyenne']:.2f}",
                        pire_moment["periode"]
                    )

                with col4:
                    st.metric(
                        "Stabilité",
                        f"{stabilite:.2f}",
                        f"Amplitude : {amplitude:.2f}"
                    )

                st.markdown("### Performance moyenne par phase de match")

                chart_blocs = (
                    alt.Chart(analyse_blocs_filtre)
                    .mark_line(point=True)
                    .encode(
                        x=alt.X(
                            "temps_debut:Q",
                            title="Temps",
                            axis=alt.Axis(
                                labelExpr="floor(datum.value/60) + ':' + (datum.value%60 < 10 ? '0' : '') + floor(datum.value%60)"
                            )
                        ),
                        y=alt.Y(
                            "evaluation_moyenne:Q",
                            title="Évaluation moyenne"
                        ),
                        tooltip=[
                            alt.Tooltip("periode:N", title="Période"),
                            alt.Tooltip("evaluation_moyenne:Q", title="Évaluation moyenne", format=".2f"),
                            alt.Tooltip("evaluation_std:Q", title="Écart-type", format=".2f"),
                            alt.Tooltip("nb_actions:Q", title="Nombre d'actions")
                        ]
                    )
                    .properties(height=350)
                )

                st.altair_chart(chart_blocs, use_container_width=True)

                st.markdown("### Détail des phases temporelles")

                st.dataframe(
                    analyse_blocs_filtre[
                        [
                            "periode",
                            "evaluation_moyenne",
                            "evaluation_std",
                            "nb_actions"
                        ]
                    ].sort_values("evaluation_moyenne", ascending=False),
                    use_container_width=True
                )

                st.markdown("### Passages forts et passages faibles")

                seuil_fort = analyse_blocs_filtre["evaluation_moyenne"].quantile(0.75)
                seuil_faible = analyse_blocs_filtre["evaluation_moyenne"].quantile(0.25)

                passages_forts = analyse_blocs_filtre[
                    analyse_blocs_filtre["evaluation_moyenne"] >= seuil_fort
                ].sort_values("evaluation_moyenne", ascending=False)

                passages_faibles = analyse_blocs_filtre[
                    analyse_blocs_filtre["evaluation_moyenne"] <= seuil_faible
                ].sort_values("evaluation_moyenne", ascending=True)

                col_fort, col_faible = st.columns(2)

                with col_fort:
                    st.markdown("#### Passages forts")
                    st.dataframe(
                        passages_forts[
                            ["periode", "score_bloc", "evaluation_moyenne", "nb_actions"]
                        ],
                        use_container_width=True
                    )

                with col_faible:
                    st.markdown("#### Passages faibles")
                    st.dataframe(
                        passages_faibles[
                            ["periode", "score_bloc", "evaluation_moyenne", "nb_actions"]
                        ],
                        use_container_width=True
                    )