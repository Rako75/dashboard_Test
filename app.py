fig_gauge.update_layout(
                    height=320, 
                    title_text="🛡️ Pourcentages de Réussite Défensive",
                    title_font=dict(color=COLORS['light'], size=16, family='Inter'),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=COLORS['light'], family='Inter')
                )
                st.plotly_chart(fig_gauge, use_container_width=True)
                
                # Graphique de comparaison défensive
                defensive_comparison = {
                    'Tacles/90': player_data['Tacles gagnants'] / (player_data['Minutes jouées'] / 90),
                    'Interceptions/90': player_data['Interceptions'] / (player_data['Minutes jouées'] / 90),
                    'Ballons récupérés/90': player_data['Ballons récupérés'] / (player_data['Minutes jouées'] / 90)
                }
                
                avg_comparison = {
                    'Tacles/90': (df_comparison['Tacles gagnants'] / (df_comparison['Minutes jouées'] / 90)).mean(),
                    'Interceptions/90': (df_comparison['Interceptions'] / (df_comparison['Minutes jouées'] / 90)).mean(),
                    'Ballons récupérés/90': (df_comparison['Ballons récupérés'] / (df_comparison['Minutes jouées'] / 90)).mean()
                }
                
                fig_def_comp = go.Figure()
                
                fig_def_comp.add_trace(go.Bar(
                    name=selected_player,
                    x=list(defensive_comparison.keys()),
                    y=list(defensive_comparison.values()),
                    marker_color=COLORS['primary'],
                    marker_line=dict(color=COLORS['light'], width=2)
                ))
                
                fig_def_comp.add_trace(go.Bar(
                    name='Moyenne compétition',
                    x=list(avg_comparison.keys()),
                    y=list(avg_comparison.values()),
                    marker_color=COLORS['secondary'],
                    marker_line=dict(color=COLORS['light'], width=2)
                ))
                
                fig_def_comp.update_layout(
                    title=dict(
                        text='📈 Actions Défensives par 90min vs Moyenne',
                        font=dict(color=COLORS['light'], size=16, family='Inter'),
                        x=0.5
                    ),
                    barmode='group',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=COLORS['light'], family='Inter'),
                    xaxis=dict(tickfont=dict(color=COLORS['light'], family='Inter')),
                    yaxis=dict(tickfont=dict(color=COLORS['light'], family='Inter'), gridcolor='rgba(255,255,255,0.2)'),
                    legend=dict(font=dict(color=COLORS['light'], family='Inter')),
                    height=420
                )
                
                st.plotly_chart(fig_def_comp, use_container_width=True)
            
            # Scatter plot pour comparaison défensive
            st.markdown("<div class='subsection-title'>🔍 Analyse Comparative Défensive</div>", unsafe_allow_html=True)
            
            col_scatter1, col_scatter2 = st.columns(2)
            
            with col_scatter1:
                metric_options_def = [
                    'Tacles gagnants', 'Interceptions', 'Ballons récupérés', 
                    'Duels aériens gagnés', 'Dégagements', 'Pourcentage de duels gagnés',
                    'Pourcentage de duels aériens gagnés'
                ]
                
                x_metric_def = st.selectbox("Métrique X", metric_options_def, index=0, key="x_def")
                y_metric_def = st.selectbox("Métrique Y", metric_options_def, index=1, key="y_def")
            
            with col_scatter2:
                fig_scatter_def = go.Figure()
                
                if x_metric_def not in ['Pourcentage de duels gagnés', 'Pourcentage de duels aériens gagnés']:
                    x_data = df_comparison[x_metric_def] / (df_comparison['Minutes jouées'] / 90)
                    x_player = player_data[x_metric_def] / (player_data['Minutes jouées'] / 90)
                    x_title = f"{x_metric_def} par 90min"
                else:
                    x_data = df_comparison[x_metric_def]
                    x_player = player_data[x_metric_def]
                    x_title = x_metric_def
                    
                if y_metric_def not in ['Pourcentage de duels gagnés', 'Pourcentage de duels aériens gagnés']:
                    y_data = df_comparison[y_metric_def] / (df_comparison['Minutes jouées'] / 90)
                    y_player = player_data[y_metric_def] / (player_data['Minutes jouées'] / 90)
                    y_title = f"{y_metric_def} par 90min"
                else:
                    y_data = df_comparison[y_metric_def]
                    y_player = player_data[y_metric_def]
                    y_title = y_metric_def
                
                fig_scatter_def.add_trace(go.Scatter(
                    x=x_data,
                    y=y_data,
                    mode='markers',
                    name='Autres joueurs',
                    marker=dict(color=COLORS['accent'], size=8, opacity=0.7, line=dict(color=COLORS['light'], width=1)),
                    text=df_comparison['Joueur'],
                    hovertemplate='<b>%{text}</b><br>' + x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
                ))
                
                fig_scatter_def.add_trace(go.Scatter(
                    x=[x_player],
                    y=[y_player],
                    mode='markers',
                    name=selected_player,
                    marker=dict(color=COLORS['primary'], size=25, symbol='star', line=dict(color=COLORS['light'], width=3)),
                    hovertemplate=f'<b>{selected_player}</b><br>' + x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
                ))
                
                fig_scatter_def.update_layout(
                    title=dict(text=f"📊 {x_title} vs {y_title}", font=dict(size=15, color=COLORS['light'], family='Inter'), x=0.5),
                    xaxis=dict(title=dict(text=x_title, font=dict(color=COLORS['light'], family='Inter')), tickfont=dict(color=COLORS['light'], family='Inter')),
                    yaxis=dict(title=dict(text=y_title, font=dict(color=COLORS['light'], family='Inter')), tickfont=dict(color=COLORS['light'], family='Inter')),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=COLORS['light'], family='Inter'),
                    legend=dict(font=dict(color=COLORS['light'], family='Inter')),
                    height=420
                )
                
                st.plotly_chart(fig_scatter_def, use_container_width=True)
            
            # Métriques défensives par 90 minutes
            st.markdown("<div class='subsection-title'>📊 Statistiques défensives par 90 min</div>", unsafe_allow_html=True)
            col1, col2, col3, col4, col5 = st.columns(5)
            
            minutes_90 = player_data['Minutes jouées'] / 90 if player_data['Minutes jouées'] > 0 else 1
            
            with col1:
                tacles_90 = player_data['Tacles gagnants'] / minutes_90
                st.metric("Tacles/90min", f"{tacles_90:.2f}")
            with col2:
                interceptions_90 = player_data['Interceptions'] / minutes_90
                st.metric("Interceptions/90min", f"{interceptions_90:.2f}")
            with col3:
                ballons_90 = player_data['Ballons récupérés'] / minutes_90
                st.metric("Ballons récupérés/90min", f"{ballons_90:.2f}")
            with col4:
                duels_90 = player_data['Duels aériens gagnés'] / minutes_90
                st.metric("Duels aériens/90min", f"{duels_90:.2f}")
            with col5:
                defensive_success = (player_data['Pourcentage de duels gagnés'] + player_data['Pourcentage de duels aériens gagnés']) / 2
                st.metric("Efficacité Défensive", f"{defensive_success:.1f}%")
        
        with tab3:
            st.markdown("<div class='section-title'>🎨 Performance Technique</div>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Graphique des actions techniques
                actions_tech = {
                    'Passes tentées': player_data['Passes tentées'],
                    'Passes progressives': player_data.get('Passes progressives', 0),
                    'Dribbles tentés': player_data['Dribbles tentés'],
                    'Touches de balle': player_data['Touches de balle'],
                    'Passes clés': player_data['Passes clés']
                }
                
                fig_bar_tech = go.Figure(data=[go.Bar(
                    x=list(actions_tech.keys()),
                    y=list(actions_tech.values()),
                    marker=dict(
                        color=COLORS['gradient'],
                        line=dict(color=COLORS['light'], width=2)
                    ),
                    text=list(actions_tech.values()),
                    textposition='outside',
                    textfont=dict(color=COLORS['light'], size=12, family='Inter')
                )])
                
                fig_bar_tech.update_layout(
                    title=dict(
                        text="🎨 Actions Techniques",
                        font=dict(size=18, color=COLORS['light'], family='Inter', weight='bold'),
                        x=0.5
                    ),
                    xaxis=dict(
                        tickfont=dict(color=COLORS['light'], family='Inter'),
                        tickangle=45
                    ),
                    yaxis=dict(
                        tickfont=dict(color=COLORS['light'], family='Inter'),
                        gridcolor='rgba(255,255,255,0.2)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=COLORS['light'], family='Inter'),
                    height=400
                )
                st.plotly_chart(fig_bar_tech, use_container_width=True)
                
                # Radar technique professionnel
                st.markdown("<div class='subsection-title'>🎨 Radar Technique Professionnel</div>", unsafe_allow_html=True)
                
                technical_metrics = {
                    'Passes tentées/90': player_data['Passes tentées'] / (player_data['Minutes jouées'] / 90),
                    'Passes prog./90': player_data.get('Passes progressives', 0) / (player_data['Minutes jouées'] / 90),
                    'Dribbles/90': player_data['Dribbles tentés'] / (player_data['Minutes jouées'] / 90),
                    'Touches/90': player_data['Touches de balle'] / (player_data['Minutes jouées'] / 90),
                    'Passes clés/90': player_data['Passes clés'] / (player_data['Minutes jouées'] / 90),
                    '% Passes réussies': player_data.get('Pourcentage de passes réussies', 0),
                    '% Dribbles réussis': player_data.get('Pourcentage de dribbles réussis', 0),
                    'Distance prog./90': player_data.get('Distance progressive des passes', 0) / (player_data['Minutes jouées'] / 90),
                    'Centres/90': player_data.get('Centres réussis', 0) / (player_data['Minutes jouées'] / 90),
                    'Courses prog./90': player_data.get('Courses progressives', 0) / (player_data['Minutes jouées'] / 90)
                }
                
                # Calculer les percentiles techniques
                tech_percentile_values = []
                tech_avg_values = []
                for metric, value in technical_metrics.items():
                    try:
                        if metric == 'Passes tentées/90':
                            distribution = df_comparison['Passes tentées'] / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Passes prog./90':
                            distribution = df_comparison.get('Passes progressives', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Dribbles/90':
                            distribution = df_comparison['Dribbles tentés'] / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Touches/90':
                            distribution = df_comparison['Touches de balle'] / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Passes clés/90':
                            distribution = df_comparison['Passes clés'] / (df_comparison['Minutes jouées'] / 90)
                        elif metric == '% Passes réussies':
                            distribution = df_comparison.get('Pourcentage de passes réussies', pd.Series([0]*len(df_comparison)))
                        elif metric == '% Dribbles réussis':
                            distribution = df_comparison.get('Pourcentage de dribbles réussis', pd.Series([0]*len(df_comparison)))
                        elif metric == 'Distance prog./90':
                            distribution = df_comparison.get('Distance progressive des passes', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Centres/90':
                            distribution = df_comparison.get('Centres réussis', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Courses prog./90':
                            distribution = df_comparison.get('Courses progressives', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                        
                        distribution = distribution.replace([np.inf, -np.inf], np.nan).dropna()
                        value = value if not np.isnan(value) and not np.isinf(value) else 0
                        
                        if len(distribution) > 0:
                            percentile = (distribution < value).mean() * 100
                            avg_comp = distribution.mean()
                        else:
                            percentile = 50
                            avg_comp = 0
                        
                        tech_percentile_values.append(min(percentile, 100))
                        tech_avg_values.append(avg_comp)
                    except:
                        tech_percentile_values.append(50)
                        tech_avg_values.append(0)
                
                # Radar technique
                fig_tech_radar = go.Figure()
                
                fig_tech_radar.add_trace(go.Scatterpolar(
                    r=tech_percentile_values,
                    theta=list(technical_metrics.keys()),
                    fill='toself',
                    fillcolor=f'rgba({46}, {125}, {50}, 0.3)',
                    line=dict(color=COLORS['success'], width=4),
                    marker=dict(color=COLORS['success'], size=10, symbol='circle'),
                    name=f'{selected_player}',
                    hovertemplate='<b>%{theta}</b><br>Percentile: %{r:.0f}<br>Valeur: %{customdata:.2f}<extra></extra>',
                    customdata=list(technical_metrics.values())
                ))
                
                # Ligne moyenne technique
                tech_avg_percentiles = []
                for i, avg_val in enumerate(tech_avg_values):
                    try:
                        if avg_val > 0:
                            metric_name = list(technical_metrics.keys())[i]
                            if metric_name == 'Passes tentées/90':
                                distribution = df_comparison['Passes tentées'] / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == 'Passes prog./90':
                                distribution = df_comparison.get('Passes progressives', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == 'Dribbles/90':
                                distribution = df_comparison['Dribbles tentés'] / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == 'Touches/90':
                                distribution = df_comparison['Touches de balle'] / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == 'Passes clés/90':
                                distribution = df_comparison['Passes clés'] / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == '% Passes réussies':
                                distribution = df_comparison.get('Pourcentage de passes réussies', pd.Series([0]*len(df_comparison)))
                            elif metric_name == '% Dribbles réussis':
                                distribution = df_comparison.get('Pourcentage de dribbles réussis', pd.Series([0]*len(df_comparison)))
                            elif metric_name == 'Distance prog./90':
                                distribution = df_comparison.get('Distance progressive des passes', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == 'Centres/90':
                                distribution = df_comparison.get('Centres réussis', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == 'Courses prog./90':
                                distribution = df_comparison.get('Courses progressives', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                            
                            distribution = distribution.replace([np.inf, -np.inf], np.nan).dropna()
                            if len(distribution) > 0:
                                avg_percentile = (distribution < avg_val).mean() * 100
                                tech_avg_percentiles.append(avg_percentile)
                            else:
                                tech_avg_percentiles.append(50)
                        else:
                            tech_avg_percentiles.append(50)
                    except:
                        tech_avg_percentiles.append(50)
                
                fig_tech_radar.add_trace(go.Scatterpolar(
                    r=tech_avg_percentiles,
                    theta=list(technical_metrics.keys()),
                    mode='lines',
                    line=dict(color='rgba(255,255,255,0.8)', width=3, dash='dash'),
                    name=f'Moyenne {selected_competition}',
                    showlegend=True,
                    hovertemplate='<b>%{theta}</b><br>Moyenne ligue: %{customdata:.2f}<extra></extra>',
                    customdata=tech_avg_values
                ))
                
                fig_tech_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100],
                            gridcolor='rgba(255,255,255,0.3)',
                            tickcolor=COLORS['light'],
                            tickfont=dict(color=COLORS['light'], size=11, family='Inter'),
                            showticklabels=True,
                            tickmode='linear',
                            tick0=0,
                            dtick=20
                        ),
                        angularaxis=dict(
                            gridcolor='rgba(255,255,255,0.3)',
                            tickcolor=COLORS['light'],
                            tickfont=dict(color=COLORS['light'], size=12, family='Inter', weight='bold'),
                            linecolor='rgba(255,255,255,0.5)'
                        ),
                        bgcolor='rgba(26, 26, 26, 0.9)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=COLORS['light'], family='Inter'),
                    title=dict(
                        text="🎨 Radar Technique Professionnel (Percentiles)",
                        font=dict(size=18, color=COLORS['light'], family='Inter', weight='bold'),
                        x=0.5,
                        y=0.95
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="center",
                        x=0.5,
                        font=dict(color=COLORS['light'], size=11, family='Inter'),
                        bgcolor='rgba(26, 26, 26, 0.8)',
                        bordercolor=COLORS['light'],
                        borderwidth=1
                    ),
                    height=480,
                    annotations=[
                        dict(
                            text=f"🏆 Performance Technique vs Moyenne {selected_competition}",
                            showarrow=False,
                            x=0.5,
                            y=-0.15,
                            xref="paper",
                            yref="paper",
                            font=dict(color=COLORS['light'], size=13, family='Inter'),
                            bgcolor=COLORS['success'],
                            bordercolor=COLORS['light'],
                            borderwidth=2,
                            borderradius=5
                        )
                    ]
                )
                
                st.plotly_chart(fig_tech_radar, use_container_width=True)
            
            with col2:
                # Pourcentages de réussite techniques
                pourcentages_tech = {
                    'Passes réussies': player_data.get('Pourcentage de passes réussies', 0),
                    'Dribbles réussis': player_data.get('Pourcentage de dribbles réussis', 0),
                    'Passes longues': player_data.get('Pourcentage de passes longues réussies', 0)
                }
                
                pourcentages_tech = {k: v if pd.notna(v) else 0 for k, v in pourcentages_tech.items()}
                
                fig_gauge_tech = make_subplots(
                    rows=1, cols=3,
                    specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
                    subplot_titles=list(pourcentages_tech.keys())
                )
                
                colors_tech = [COLORS['success'], COLORS['warning'], COLORS['primary']]
                for i, (metric, value) in enumerate(pourcentages_tech.items()):
                    fig_gauge_tech.add_trace(
                        go.Indicator(
                            mode="gauge+number",
                            value=value,
                            gauge=dict(
                                axis=dict(range=[0, 100]),
                                bar=dict(color=colors_tech[i], thickness=0.3),
                                bgcolor="rgba(26, 26, 26, 0.8)",
                                borderwidth=3,
                                bordercolor=COLORS['light'],
                                steps=[
                                    {'range': [0, 50], 'color': 'rgba(255,255,255,0.1)'},
                                    {'range': [50, 80], 'color': 'rgba(255,255,255,0.2)'},
                                    {'range': [80, 100], 'color': 'rgba(255,255,255,0.3)'}
                                ]
                            ),
                            number={'suffix': '%', 'font': {'color': COLORS['light'], 'family': 'Inter', 'size': 16}}
                        ),
                        row=1, col=i+1
                    )
                
                fig_gauge_tech.update_layout(
                    height=320, 
                    title_text="🎨 Pourcentages de Réussite Technique",
                    title_font=dict(color=COLORS['light'], size=16, family='Inter'),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=COLORS['light'], family='Inter')
                )
                st.plotly_chart(fig_gauge_tech, use_container_width=True)
                
                # Graphique de comparaison technique
                technical_comparison = {
                    'Passes/90': player_data['Passes tentées'] / (player_data['Minutes jouées'] / 90),
                    'Dribbles/90': player_data['Dribbles tentés'] / (player_data['Minutes jouées'] / 90),
                    'Touches/90': player_data['Touches de balle'] / (player_data['Minutes jouées'] / 90)
                }
                
                avg_comparison_tech = {
                    'Passes/90': (df_comparison['Passes tentées'] / (df_comparison['Minutes jouées'] / 90)).mean(),
                    'Dribbles/90': (df_comparison['Dribbles tentés'] / (df_comparison['Minutes jouées'] / 90)).mean(),
                    'Touches/90': (df_comparison['Touches de balle'] / (df_comparison['Minutes jouées'] / 90)).mean()
                }
                
                fig_tech_comp = go.Figure()
                
                fig_tech_comp.add_trace(go.Bar(
                    name=selected_player,
                    x=list(technical_comparison.keys()),
                    y=list(technical_comparison.values()),
                    marker_color=COLORS['primary'],
                    marker_line=dict(color=COLORS['light'], width=2)
                ))
                
                fig_tech_comp.add_trace(go.Bar(
                    name='Moyenne compétition',
                    x=list(avg_comparison_tech.keys()),
                    y=list(avg_comparison_tech.values()),
                    marker_color=COLORS['secondary'],
                    marker_line=dict(color=COLORS['light'], width=2)
                ))
                
                fig_tech_comp.update_layout(
                    title=dict(
                        text='📈 Actions Techniques par 90min vs Moyenne',
                        font=dict(color=COLORS['light'], size=16, family='Inter'),
                        x=0.5
                    ),
                    barmode='group',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=COLORS['light'], family='Inter'),
                    xaxis=dict(tickfont=dict(color=COLORS['light'], family='Inter')),
                    yaxis=dict(tickfont=dict(color=COLORS['light'], family='Inter'), gridcolor='rgba(255,255,255,0.2)'),
                    legend=dict(font=dict(color=COLORS['light'], family='Inter')),
                    height=420
                )
                
                st.plotly_chart(fig_tech_comp, use_container_width=True)
            
            # Scatter plot pour comparaison technique
            st.markdown("<div class='subsection-title'>🔍 Analyse Comparative Technique</div>", unsafe_allow_html=True)
            
            col_scatter1, col_scatter2 = st.columns(2)
            
            with col_scatter1:
                metric_options_tech = [
                    'Passes tentées', 'Pourcentage de passes réussies', 'Passes progressives',
                    'Passes clés', 'Dribbles tentés', 'Pourcentage de dribbles réussis',
                    'Touches de balle', 'Distance progressive des passes'
                ]
                
                x_metric_tech = st.selectbox("Métrique X", metric_options_tech, index=0, key="x_tech")
                y_metric_tech = st.selectbox("Métrique Y", metric_options_tech, index=1, key="y_tech")
            
            with col_scatter2:
                fig_scatter_tech = go.Figure()
                
                if 'Pourcentage' not in x_metric_tech:
                    x_data = df_comparison[x_metric_tech] / (df_comparison['Minutes jouées'] / 90)
                    x_player = player_data[x_metric_tech] / (player_data['Minutes jouées'] / 90)
                    x_title = f"{x_metric_tech} par 90min"
                else:
                    x_data = df_comparison[x_metric_tech]
                    x_player = player_data[x_metric_tech]
                    x_title = x_metric_tech
                    
                if 'Pourcentage' not in y_metric_tech:
                    y_data = df_comparison[y_metric_tech] / (df_comparison['Minutes jouées'] / 90)
                    y_player = player_data[y_metric_tech] / (player_data['Minutes jouées'] / 90)
                    y_title = f"{y_metric_tech} par 90min"
                else:
                    y_data = df_comparison[y_metric_tech]
                    y_player = player_data[y_metric_tech]
                    y_title = y_metric_tech
                
                fig_scatter_tech.add_trace(go.Scatter(
                    x=x_data,
                    y=y_data,
                    mode='markers',
                    name='Autres joueurs',
                    marker=dict(color=COLORS['accent'], size=8, opacity=0.7, line=dict(color=COLORS['light'], width=1)),
                    text=df_comparison['Joueur'],
                    hovertemplate='<b>%{text}</b><br>' + x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
                ))
                
                fig_scatter_tech.add_trace(go.Scatter(
                    x=[x_player],
                    y=[y_player],
                    mode='markers',
                    name=selected_player,
                    marker=dict(color=COLORS['primary'], size=25, symbol='star', line=dict(color=COLORS['light'], width=3)),
                    hovertemplate=f'<b>{selected_player}</b><br>' + x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
                ))
                
                fig_scatter_tech.update_layout(
                    title=dict(text=f"📊 {x_title} vs {y_title}", font=dict(size=15, color=COLORS['light'], family='Inter'), x=0.5),
                    xaxis=dict(title=dict(text=x_title, font=dict(color=COLORS['light'], family='Inter')), tickfont=dict(color=COLORS['light'], family='Inter')),
                    yaxis=dict(title=dict(text=y_title, font=dict(color=COLORS['light'], family='Inter')), tickfont=dict(color=COLORS['light'], family='Inter')),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=COLORS['light'], family='Inter'),
                    legend=dict(font=dict(color=COLORS['light'], family='Inter')),
                    height=420
                )
                
                st.plotly_chart(fig_scatter_tech, use_container_width=True)
            
            # Métriques techniques détaillées
            st.markdown("<div class='subsection-title'>📊 Statistiques Techniques Détaillées</div>", unsafe_allow_html=True)
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Distance passes", f"{player_data.get('Distance totale des passes', 0):.0f}m")
                st.metric("Distance progressive", f"{player_data.get('Distance progressive des passes', 0):.0f}m")
            
            with col2:
                st.metric("Passes tentées", f"{player_data.get('Passes tentées', 0):.0f}")
                st.metric("% Réussite passes", f"{player_data.get('Pourcentage de passes réussies', 0):.1f}%")
            
            with col3:
                touches_90 = player_data['Touches de balle'] / (player_data['Minutes jouées'] / 90)
                st.metric("Touches/90min", f"{touches_90:.1f}")
                st.metric("Passes clés", f"{player_data.get('Passes clés', 0):.0f}")
            
            with col4:
                distance_portee = player_data.get('Distance totale parcourue avec le ballon (en mètres)', 0)
                st.metric("Distance portée", f"{distance_portee:.0f}m")
                st.metric("Centres dans surface", f"{player_data.get('Centres dans la surface', 0):.0f}")
            
            with col5:
                passes_critiques = (player_data.get('Pourcentage de passes longues réussies', 0) + 
                                   player_data.get('Pourcentage de passes courtes réussies', 0)) / 2
                st.metric("Précision Zones Critiques", f"{passes_critiques:.1f}%")
        
        with tab4:
            st.markdown("<div class='section-title'>🔄 Comparaison Pizza Chart</div>", unsafe_allow_html=True)
            
            # Choix du mode avec style football
            mode = st.radio("Mode de visualisation", ["Radar individuel", "Radar comparatif"], horizontal=True)
            
            font_normal = FontManager()
            font_bold = FontManager()
            font_italic = FontManager()
            
            if mode == "Radar individuel":
                st.markdown(f"<div class='subsection-title'>🎯 Radar individuel : {selected_player}</div>", unsafe_allow_html=True)
                
                try:
                    values1 = calculate_percentiles(selected_player, df_comparison)
                    
                    baker = PyPizza(
                        params=list(RAW_STATS.keys()),
                        background_color="#1A1A1A",
                        straight_line_color=COLORS['light'],
                        straight_line_lw=2,
                        last_circle_color=COLORS['light'],
                        last_circle_lw=2,
                        other_circle_lw=1,
                        other_circle_color='rgba(255,255,255,0.3)',
                        inner_circle_size=15
                    )
                    
                    fig, ax = baker.make_pizza(
                        values1,
                        figsize=(14, 16),
                        param_location=110,
                        color_blank_space="same",
                        slice_colors=[COLORS['primary']] * len(values1),
                        value_colors=[COLORS['light']] * len(values1),
                        value_bck_colors=[COLORS['primary']] * len(values1),
                        kwargs_slices=dict(edgecolor=COLORS['light'], zorder=2, linewidth=2),
                        kwargs_params=dict(color=COLORS['light'], fontsize=14, fontproperties=font_bold.prop, weight='bold'),
                        kwargs_values=dict(color=COLORS['light'], fontsize=12, fontproperties=font_normal.prop,
                                           bbox=dict(edgecolor=COLORS['light'], facecolor=COLORS['primary'], boxstyle="round,pad=0.3", lw=2))
                    )
                    
                    # Titre principal avec style football
                    fig.text(0.515, 0.97, f"⚽ {selected_player}", size=28, ha="center", 
                             fontproperties=font_bold.prop, color=COLORS['light'], weight='bold')
                    fig.text(0.515, 0.94, f"🏆 Radar Individuel | Percentile | {selected_competition} 2024-25", size=16,
                             ha="center", fontproperties=font_bold.prop, color=COLORS['accent'])
                    
                    # Logo et source avec style professionnel
                    fig.text(0.99, 0.02, "🏟️ Football Analytics Pro | Source: FBRef",
                             size=10, ha="right", fontproperties=font_italic.prop, color=COLORS['accent'])
                    
                    # Ajouter des lignes de terrain en arrière-plan
                    fig.patch.set_facecolor('#1A1A1A')
                    
                    st.pyplot(fig, bbox_inches='tight', facecolor='#1A1A1A')
                    
                except Exception as e:
                    st.error(f"Erreur lors de la création du radar individuel : {str(e)}")
            
            elif mode == "Radar comparatif":
                col1, col2 = st.columns(2)
                
                with col1:
                    ligue1 = st.selectbox("🏆 Ligue Joueur 1", competitions, 
                                         index=competitions.index(selected_competition), key="ligue1_comp")
                    df_j1 = df[df['Compétition'] == ligue1]
                    joueur1 = st.selectbox("👤 Joueur 1", df_j1['Joueur'].sort_values(), 
                                          index=list(df_j1['Joueur'].sort_values()).index(selected_player), key="joueur1_comp")
                
                with col2:
                    ligue2 = st.selectbox("🏆 Ligue Joueur 2", competitions, key="ligue2_comp")
                    df_j2 = df[df['Compétition'] == ligue2]
                    joueur2 = st.selectbox("👤 Joueur 2", df_j2['Joueur'].sort_values(), key="joueur2_comp")
                
                if joueur1 and joueur2:
                    st.markdown(f"<div class='subsection-title'>⚔️ Radar comparatif : {joueur1} vs {joueur2}</div>", unsafe_allow_html=True)
                    
                    try:
                        values1 = calculate_percentiles(joueur1, df_j1)
                        values2 = calculate_percentiles(joueur2, df_j2)
                        
                        params_offset = [False] * len(RAW_STATS)
                        if len(params_offset) > 9:
                            params_offset[9] = True
                        if len(params_offset) > 10:
                            params_offset[10] = True
                        
                        baker = PyPizza(
                            params=list(RAW_STATS.keys()),
                            background_color="#1A1A1A",
                            straight_line_color=COLORS['light'],
                            straight_line_lw=2,
                            last_circle_color=COLORS['light'],
                            last_circle_lw=2,
                            other_circle_ls="-.",
                            other_circle_lw=1,
                            other_circle_color='rgba(255,255,255,0.3)'
                        )
                        
                        fig, ax = baker.make_pizza(
                            values1,
                            compare_values=values2,
                            figsize=(14, 14),
                            kwargs_slices=dict(facecolor=COLORS['primary'], edgecolor=COLORS['light'], linewidth=2, zorder=2, alpha=0.8),
                            kwargs_compare=dict(facecolor=COLORS['secondary'], edgecolor=COLORS['light'], linewidth=2, zorder=2, alpha=0.8),
                            kwargs_params=dict(color=COLORS['light'], fontsize=14, fontproperties=font_bold.prop, weight='bold'),
                            kwargs_values=dict(
                                color=COLORS['light'], fontsize=12, fontproperties=font_normal.prop, zorder=3,
                                bbox=dict(edgecolor=COLORS['light'], facecolor=COLORS['primary'], boxstyle="round,pad=0.3", lw=2)
                            ),
                            kwargs_compare_values=dict(
                                color=COLORS['light'], fontsize=12, fontproperties=font_normal.prop, zorder=3,
                                bbox=dict(edgecolor=COLORS['light'], facecolor=COLORS['secondary'], boxstyle="round,pad=0.3", lw=2)
                            )
                        )
                        
                        try:
                            baker.adjust_texts(params_offset, offset=-0.17, adj_comp_values=True)
                        except:
                            pass
                        
                        # Titre principal comparatif
                        fig.text(0.515, 0.97, "⚽ Radar Comparatif Football", size=24, ha="center", 
                                 fontproperties=font_bold.prop, color=COLORS['light'], weight='bold')
                        fig.text(0.515, 0.94, f"🏆 Percentile | Saison 2024-25", size=16,
                                 ha="center", fontproperties=font_bold.prop, color=COLORS['accent'])
                        
                        # Légende avec style football
                        legend_p1 = mpatches.Patch(color=COLORS['primary'], label=f"🔵 {joueur1}")
                        legend_p2 = mpatches.Patch(color=COLORS['secondary'], label=f"🔴 {joueur2}")
                        legend = ax.legend(handles=[legend_p1, legend_p2], loc="upper right", bbox_to_anchor=(1.35, 1.0),
                                         fontsize=12, frameon=True, facecolor='#1A1A1A', edgecolor=COLORS['light'])
                        legend.get_frame().set_alpha(0.9)
                        
                        fig.text(0.99, 0.02, "🏟️ Football Analytics Pro | Source: FBRef\nInspiration: @Worville, @FootballSlices",
                                 size=9, ha="right", fontproperties=font_italic.prop, color=COLORS['accent'])
                        
                        fig.patch.set_facecolor('#1A1A1A')
                        
                        st.pyplot(fig, bbox_inches='tight', facecolor='#1A1A1A')
                        
                    except Exception as e:
                        st.error(f"Erreur lors de la création du radar comparatif : {str(e)}")

    else:
        st.warning("Veuillez ajuster les filtres pour sélectionner un joueur.")

    # Footer avec design football professionnel
    st.markdown("---")
    st.markdown("""
    <div class='football-footer'>
        <p style='font-size: 1.3em; font-weight: 600; margin-bottom: 10px;'>
            🏟️ Football Analytics Pro - Dashboard Professionnel
        </p>
        <p style='font-size: 1em; opacity: 0.9;'>
            📊 Analyse avancée des performances | 🏆 Données: FBRef | ⚽ Saison 2024-25
        </p>
        <p style='font-size: 0.9em; opacity: 0.7; margin-top: 10px;'>
            🎯 Développé pour les professionnels du football
        </p>
    </div>
    """, unsafe_allow_html=True)

else:
    # Message d'erreur avec design football
    st.markdown("""
    <div style='text-align: center; padding: 3rem; background: linear-gradient(135deg, #D32F2F 0%, #FF6B35 100%); 
                border-radius: 20px; margin: 2rem 0; border: 3px solid #FFFFFF; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);'>
        <h2 style='color: white; margin: 0; font-size: 2.5em; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);'>
            ⚠️ Erreur de chargement des données
        </h2>
        <p style='color: #FFE8E8; margin: 20px 0 0 0; font-size: 1.3em; font-weight: 500;'>
            🏟️ Impossible de charger les données du terrain. Veuillez vérifier que le fichier 'df_BIG2025.csv' est présent.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 Ce dashboard football nécessite un fichier CSV avec les statistiques des joueurs pour fonctionner correctement.")
                            
            with col2:
                # Pourcentages de réussite défensifs
                pourcentages = {
                    'Duels aériens': player_data['Pourcentage de duels aériens gagnés'],
                    'Duels défensifs': player_data['Pourcentage de duels gagnés'],
                    'Passes réussies': player_data['Pourcentage de passes réussies']
                }
                
                pourcentages = {k: v if pd.notna(v) else 0 for k, v in pourcentages.items()}
                
                fig_gauge = make_subplots(
                    rows=1, cols=3,
                    specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
                    subplot_titles=list(pourcentages.keys())
                )
                
                colors = [COLORS['danger'], COLORS['secondary'], COLORS['success']]
                for i, (metric, value) in enumerate(pourcentages.items()):
                    fig_gauge.add_trace(
                        go.Indicator(
                            mode="gauge+number",
                            value=value,
                            gauge=dict(
                                axis=dict(range=[0, 100]),
                                bar=dict(color=colors[i], thickness=0.3),
                                bgcolor="rgba(26, 26, 26, 0.8)",
                                borderwidth=3,
                                bordercolor=COLORS['light'],
                                steps=[
                                    {'range': [0, 50], 'color': 'rgba(255,255,255,0.1)'},
                                    {'range': [50, 80], 'color': 'rgba(255,255,255,0.2)'},
                                    {'range': [80, 100], 'color': 'rgba(255,255,255,0.3)'}
                                ]
                            ),
                            number={'suffix': '%', 'font': {'color': COLORS['light'], 'family': 'Inter', 'size': 16}}
                        ),
                        row=1, col=i+1
                    )
                
                fig_gauge.update_layout(
                    height=320, 
                    title_text="🛡️ Pourcentages de Réussite Défensive",
                    title_font=dict(color=COLORS['light'], size=16, family='Inter'),
                    paper_bgcolor='rgba(0,0,0,0)',import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from mplsoccer import PyPizza, FontManager
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Configuration de la page avec thème football
st.set_page_config(
    page_title="⚽ Football Analytics Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un thème football professionnel
st.markdown("""
<style>
    /* Import Google Fonts pour un look professionnel */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Variables CSS pour cohérence */
    :root {
        --primary-green: #00A86B;
        --dark-green: #006B3C;
        --light-green: #4CAF50;
        --football-brown: #8B4513;
        --field-green: #2E7D32;
        --grass-green: #388E3C;
        --white-lines: #FFFFFF;
        --dark-bg: #1A1A1A;
        --card-bg: #2D2D2D;
        --text-primary: #FFFFFF;
        --text-secondary: #B0B0B0;
        --accent-orange: #FF6B35;
    }
    
    /* Background principal */
    .main {
        background: linear-gradient(135deg, var(--dark-bg) 0%, var(--field-green) 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(
            135deg, 
            var(--dark-bg) 0%, 
            var(--field-green) 30%, 
            var(--grass-green) 70%, 
            var(--dark-green) 100%
        );
    }
    
    /* Header principal */
    .football-header {
        background: linear-gradient(135deg, var(--primary-green) 0%, var(--dark-green) 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 3px solid var(--white-lines);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .football-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: 
            repeating-linear-gradient(
                90deg,
                transparent 0px,
                transparent 48px,
                rgba(255, 255, 255, 0.1) 50px,
                rgba(255, 255, 255, 0.1) 52px
            );
        pointer-events: none;
    }
    
    .football-header h1 {
        color: var(--text-primary);
        font-weight: 700;
        font-size: 3.5em;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        margin: 0;
        position: relative;
        z-index: 1;
    }
    
    .football-header p {
        color: var(--text-secondary);
        font-size: 1.3em;
        margin: 10px 0 0 0;
        position: relative;
        z-index: 1;
    }
    
    /* Sidebar football */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, var(--card-bg) 0%, var(--field-green) 100%);
    }
    
    .football-sidebar-header {
        background: linear-gradient(135deg, var(--primary-green) 0%, var(--dark-green) 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        border: 2px solid var(--white-lines);
        text-align: center;
    }
    
    .football-sidebar-header h2 {
        color: var(--text-primary);
        margin: 0;
        font-weight: 600;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
    }
    
    /* Onglets style football */
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(135deg, var(--card-bg) 0%, var(--field-green) 100%);
        border-radius: 15px;
        padding: 10px;
        border: 2px solid var(--white-lines);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: var(--text-primary);
        border-radius: 10px;
        font-weight: 500;
        padding: 12px 20px;
        margin: 0 5px;
        transition: all 0.3s ease;
        border: 1px solid transparent;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid var(--white-lines);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-green) 0%, var(--light-green) 100%);
        color: var(--text-primary);
        border: 1px solid var(--white-lines);
        box-shadow: 0 3px 10px rgba(0, 168, 107, 0.4);
    }
    
    /* Cartes métriques style football */
    .metric-card {
        background: linear-gradient(135deg, var(--card-bg) 0%, var(--field-green) 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid var(--white-lines);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        margin: 10px 0;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-green) 0%, var(--light-green) 100%);
    }
    
    .stMetric {
        background: linear-gradient(135deg, var(--card-bg) 0%, var(--field-green) 100%);
        padding: 1.2rem;
        border-radius: 12px;
        border: 2px solid var(--white-lines);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        margin: 5px 0;
        transition: transform 0.2s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }
    
    .stMetric-value {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 1.8em !important;
    }
    
    .stMetric-label {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
    }
    
    /* Section profil joueur */
    .player-profile {
        background: linear-gradient(135deg, var(--card-bg) 0%, var(--field-green) 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        border: 3px solid var(--primary-green);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        position: relative;
    }
    
    .player-profile::before {
        content: '⚽';
        position: absolute;
        top: 20px;
        right: 20px;
        font-size: 2em;
        opacity: 0.3;
    }
    
    .player-profile h2 {
        color: var(--primary-green);
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    }
    
    /* Section titres */
    .section-title {
        background: linear-gradient(135deg, var(--primary-green) 0%, var(--dark-green) 100%);
        color: var(--text-primary);
        padding: 1rem 2rem;
        border-radius: 12px;
        margin: 2rem 0 1rem 0;
        border: 2px solid var(--white-lines);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        font-weight: 600;
        text-align: center;
    }
    
    /* Sous-titres */
    .subsection-title {
        color: var(--light-green);
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        padding: 0.8rem 1.5rem;
        background: linear-gradient(135deg, var(--card-bg) 0%, rgba(76, 175, 80, 0.2) 100%);
        border-radius: 10px;
        border-left: 4px solid var(--light-green);
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
    }
    
    /* Footer football */
    .football-footer {
        background: linear-gradient(135deg, var(--card-bg) 0%, var(--field-green) 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-top: 3rem;
        border: 2px solid var(--white-lines);
        text-align: center;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }
    
    .football-footer p {
        color: var(--text-primary);
        margin: 0.5rem 0;
        font-weight: 500;
    }
    
    /* Selectbox style football */
    .stSelectbox > div > div {
        background: linear-gradient(135deg, var(--card-bg) 0%, var(--field-green) 100%);
        border: 2px solid var(--white-lines);
        border-radius: 10px;
        color: var(--text-primary);
    }
    
    /* Slider style football */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, var(--primary-green) 0%, var(--light-green) 100%);
    }
    
    /* Radio buttons style football */
    .stRadio > div {
        background: linear-gradient(135deg, var(--card-bg) 0%, rgba(46, 125, 50, 0.3) 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid var(--white-lines);
    }
    
    /* Messages d'erreur/info style football */
    .stAlert > div {
        background: linear-gradient(135deg, var(--card-bg) 0%, rgba(255, 107, 53, 0.2) 100%);
        border: 2px solid var(--accent-orange);
        border-radius: 10px;
        color: var(--text-primary);
    }
    
    /* Animation terrain de football */
    @keyframes grass-wave {
        0%, 100% { opacity: 0.8; }
        50% { opacity: 1; }
    }
    
    .grass-animation {
        animation: grass-wave 3s ease-in-out infinite;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .football-header h1 {
            font-size: 2.5em;
        }
        
        .football-header p {
            font-size: 1.1em;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 8px 12px;
            font-size: 0.9em;
        }
    }
</style>
""", unsafe_allow_html=True)

# Couleurs professionnelles thème football
COLORS = {
    'primary': '#00A86B',      # Vert terrain principal
    'secondary': '#006B3C',    # Vert foncé
    'accent': '#4CAF50',       # Vert clair
    'success': '#2E7D32',      # Vert succès
    'warning': '#FF6B35',      # Orange accent
    'danger': '#D32F2F',       # Rouge
    'dark': '#1A1A1A',         # Noir principal
    'light': '#FFFFFF',        # Blanc lignes
    'gradient': ['#00A86B', '#006B3C', '#4CAF50', '#2E7D32', '#FF6B35']  # Palette football
}

# ---------------------- PARAMÈTRES DU RADAR ----------------------

RAW_STATS = {
    "Buts\nsans pénalty": "Buts (sans penalty)",
    "Passes déc.": "Passes décisives",
    "Buts +\nPasses déc.": "Buts + Passes D",
    "Cartons\njaunes": "Cartons jaunes",
    "Cartons\nrouges": "Cartons rouges",
    "Passes\ntentées": "Passes tentées",
    "Passes\nclés": "Passes clés",
    "Passes\nprogressives": "Passes progressives",
    "Passes\ndernier 1/3": "Passes dans le dernier tiers",
    "Passes\ndans la surface": "Passes dans la surface",
    "Touches": "Touches de balle",
    "Dribbles\ntentés": "Dribbles tentés",
    "Dribbles\nréussis": "Dribbles réussis",
    "Ballons perdus\nsous pression": "Ballons perdus sous la pression d'un adversaire",
    "Ballons perdus\nen conduite": "Ballons perdus en conduite",
    "Tacles\ngagnants": "Tacles gagnants",
    "Tirs\nbloqués": "Tirs bloqués",
    "Duels\ngagnés": "Duels défensifs gagnés",
    "Interceptions": "Interceptions",
    "Dégagements": "Dégagements"
}

COLOR_1 = COLORS['primary']
COLOR_2 = COLORS['secondary']
SLICE_COLORS = [COLORS['accent']] * len(RAW_STATS)

def calculate_percentiles(player_name, df):
    """Calcule les percentiles pour le pizza chart"""
    player = df[df["Joueur"] == player_name].iloc[0]
    percentiles = []

    for label, col in RAW_STATS.items():
        try:
            if col not in df.columns or pd.isna(player[col]):
                percentile = 0
            elif "par 90 minutes" in col or "%" in col:
                val = player[col]
                dist = df[col]
                if pd.isna(val) or dist.dropna().empty:
                    percentile = 0
                else:
                    percentile = round((dist < val).mean() * 100)
            else:
                if player.get("Matchs en 90 min", 0) == 0:
                    matches = player.get("Matchs joués", 1)
                    if matches == 0:
                        percentile = 0
                    else:
                        val = player[col] / matches
                        dist = df[col] / df.get("Matchs joués", 1)
                        if pd.isna(val) or dist.dropna().empty:
                            percentile = 0
                        else:
                            percentile = round((dist < val).mean() * 100)
                else:
                    val = player[col] / player["Matchs en 90 min"]
                    dist = df[col] / df["Matchs en 90 min"]
                    if pd.isna(val) or dist.dropna().empty:
                        percentile = 0
                    else:
                        percentile = round((dist < val).mean() * 100)
        except Exception as e:
            percentile = 0
        percentiles.append(percentile)

    return percentiles

@st.cache_data
def load_data():
    """Charge les données depuis le fichier CSV"""
    try:
        df = pd.read_csv('df_BIG2025.csv', encoding='utf-8')
        return df
    except FileNotFoundError:
        st.error("Fichier 'df_BIG2025.csv' non trouvé. Veuillez vous assurer que le fichier est dans le même répertoire.")
        return None
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {str(e)}")
        return None

# Chargement des données
df = load_data()

if df is not None:
    # Header avec design football professionnel
    st.markdown("""
    <div class='football-header'>
        <h1>⚽ Football Analytics Pro</h1>
        <p>🏆 Analyse professionnelle des performances - Saison 2024-25</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar avec design football
    with st.sidebar:
        st.markdown("""
        <div class='football-sidebar-header'>
            <h2>🎯 Sélection du joueur</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Sélection de la compétition/ligue
        competitions = sorted(df['Compétition'].dropna().unique())
        selected_competition = st.selectbox(
            "🏆 Choisir une compétition :",
            competitions,
            index=0
        )
        
        # Filtrer les joueurs selon la compétition
        df_filtered = df[df['Compétition'] == selected_competition]
        
        # Filtre par minutes jouées
        min_minutes = int(df_filtered['Minutes jouées'].min()) if not df_filtered['Minutes jouées'].empty else 0
        max_minutes = int(df_filtered['Minutes jouées'].max()) if not df_filtered['Minutes jouées'].empty else 3000
        
        st.markdown("---")
        st.markdown("**⏱️ Filtrer par minutes jouées :**")
        
        # Slider pour sélectionner le minimum de minutes
        min_minutes_filter = st.slider(
            "Minutes minimum jouées :",
            min_value=min_minutes,
            max_value=max_minutes,
            value=min_minutes,
            step=90,
            help="Filtrer les joueurs ayant joué au minimum ce nombre de minutes"
        )
        
        # Filtrer les joueurs selon les minutes jouées
        df_filtered_minutes = df_filtered[df_filtered['Minutes jouées'] >= min_minutes_filter]
        
        # Afficher le nombre de joueurs après filtrage
        nb_joueurs = len(df_filtered_minutes)
        st.markdown(f"📊 **{nb_joueurs} joueurs** correspondent aux critères")
        
        st.markdown("---")
        
        # Sélection du joueur (maintenant filtré par minutes)
        if not df_filtered_minutes.empty:
            joueurs = sorted(df_filtered_minutes['Joueur'].dropna().unique())
            selected_player = st.selectbox(
                "👤 Choisir un joueur :",
                joueurs,
                index=0
            )
        else:
            st.error("Aucun joueur ne correspond aux critères sélectionnés.")
            selected_player = None
    
    # Obtenir les données du joueur sélectionné
    if selected_player:
        player_data = df_filtered_minutes[df_filtered_minutes['Joueur'] == selected_player].iloc[0]
        
        # Utiliser df_filtered_minutes pour les comparaisons et calculs
        df_comparison = df_filtered_minutes
    
        # Affichage des informations générales du joueur avec design football
        st.markdown(f"""
        <div class='player-profile'>
            <h2>📊 Profil de {selected_player}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Âge", f"{player_data['Âge']} ans")
        with col2:
            st.metric("Position", player_data['Position'])
        with col3:
            st.metric("Équipe", player_data['Équipe'])
        with col4:
            st.metric("Nationalité", player_data['Nationalité'])
        with col5:
            st.metric("Minutes jouées", f"{int(player_data['Minutes jouées'])} min")
        
        st.markdown("---")
    
        # Graphiques principaux avec onglets style football
        tab1, tab2, tab3, tab4 = st.tabs(["🎯 Performance Offensive", "🛡️ Performance Défensive", "🎨 Performance Technique", "🔄 Comparer Joueurs"])
        
        with tab1:
            st.markdown("<div class='section-title'>🎯 Performance Offensive</div>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Graphique des actions offensives
                actions_off = {
                    'Buts': player_data['Buts'],
                    'Passes décisives': player_data['Passes décisives'],
                    'Passes clés': player_data['Passes clés'],
                    'Actions → Tir': player_data.get('Actions menant à un tir', 0),
                    'Tirs': player_data.get('Tirs', 0)
                }
                
                fig_bar_off = go.Figure(data=[go.Bar(
                    x=list(actions_off.keys()),
                    y=list(actions_off.values()),
                    marker=dict(
                        color=COLORS['gradient'],
                        line=dict(color=COLORS['light'], width=2)
                    ),
                    text=list(actions_off.values()),
                    textposition='outside',
                    textfont=dict(color=COLORS['light'], size=12, family='Inter')
                )])
                
                fig_bar_off.update_layout(
                    title=dict(
                        text="Actions Offensives",
                        font=dict(size=18, color=COLORS['light'], family='Inter', weight='bold'),
                        x=0.5
                    ),
                    xaxis=dict(
                        tickfont=dict(color=COLORS['light'], family='Inter'),
                        tickangle=45,
                        gridcolor='rgba(255,255,255,0.1)'
                    ),
                    yaxis=dict(
                        tickfont=dict(color=COLORS['light'], family='Inter'),
                        gridcolor='rgba(255,255,255,0.2)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=COLORS['light'], family='Inter'),
                    height=400
                )
                st.plotly_chart(fig_bar_off, use_container_width=True)
                
                # Radar offensif professionnel
                st.markdown("<div class='subsection-title'>🎯 Radar Offensif Professionnel</div>", unsafe_allow_html=True)
                
                offensive_metrics = {
                    'Buts/90': player_data['Buts par 90 minutes'],
                    'Passes D./90': player_data['Passes décisives par 90 minutes'],
                    'xG/90': player_data['Buts attendus par 90 minutes'],
                    'xA/90': player_data['Passes décisives attendues par 90 minutes'],
                    'Tirs/90': player_data['Tirs par 90 minutes'],
                    'Passes clés/90': player_data['Passes clés'] / (player_data['Minutes jouées'] / 90),
                    'Dribbles réussis/90': player_data['Dribbles réussis'] / (player_data['Minutes jouées'] / 90),
                    'Actions → Tir/90': player_data['Actions menant à un tir par 90 minutes'],
                    'Passes dernier tiers/90': player_data.get('Passes dans le dernier tiers', 0) / (player_data['Minutes jouées'] / 90),
                    'Passes prog./90': player_data.get('Passes progressives', 0) / (player_data['Minutes jouées'] / 90)
                }
                
                # Calculer les percentiles par rapport à la compétition
                percentile_values = []
                avg_values = []
                for metric, value in offensive_metrics.items():
                    if metric.endswith('/90'):
                        if metric == 'Buts/90':
                            distribution = df_comparison['Buts par 90 minutes']
                        elif metric == 'Passes D./90':
                            distribution = df_comparison['Passes décisives par 90 minutes']
                        elif metric == 'xG/90':
                            distribution = df_comparison['Buts attendus par 90 minutes']
                        elif metric == 'xA/90':
                            distribution = df_comparison['Passes décisives attendues par 90 minutes']
                        elif metric == 'Tirs/90':
                            distribution = df_comparison['Tirs par 90 minutes']
                        elif metric == 'Actions → Tir/90':
                            distribution = df_comparison['Actions menant à un tir par 90 minutes']
                        elif metric == 'Passes dernier tiers/90':
                            distribution = df_comparison['Passes dans le dernier tiers'] / (df_comparison['Minutes jouées'] / 90)
                        else:
                            base_column = metric.replace('/90', '').replace('Passes D.', 'Passes décisives').replace('Passes prog.', 'Passes progressives')
                            distribution = df_comparison[base_column] / (df_comparison['Minutes jouées'] / 90)
                        
                        percentile = (distribution < value).mean() * 100
                        avg_comp = distribution.mean()
                        percentile_values.append(min(percentile, 100))
                        avg_values.append(avg_comp)
                    else:
                        percentile_values.append(50)
                        avg_values.append(0)
                
                # Créer le radar avec style football
                fig_radar = go.Figure()
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=percentile_values,
                    theta=list(offensive_metrics.keys()),
                    fill='toself',
                    fillcolor=f'rgba({0}, {168}, {107}, 0.3)',
                    line=dict(color=COLORS['primary'], width=4),
                    marker=dict(color=COLORS['primary'], size=10, symbol='circle'),
                    name=f'{selected_player}',
                    hovertemplate='<b>%{theta}</b><br>Percentile: %{r:.0f}<br>Valeur: %{customdata:.2f}<extra></extra>',
                    customdata=list(offensive_metrics.values())
                ))
                
                # Ligne de référence moyenne
                avg_percentiles = []
                for i, avg_val in enumerate(avg_values):
                    if avg_val > 0:
                        metric_name = list(offensive_metrics.keys())[i]
                        if metric_name == 'Buts/90':
                            distribution = df_comparison['Buts par 90 minutes']
                        elif metric_name == 'Passes D./90':
                            distribution = df_comparison['Passes décisives par 90 minutes']
                        elif metric_name == 'xG/90':
                            distribution = df_comparison['Buts attendus par 90 minutes']
                        elif metric_name == 'xA/90':
                            distribution = df_comparison['Passes décisives attendues par 90 minutes']
                        elif metric_name == 'Tirs/90':
                            distribution = df_comparison['Tirs par 90 minutes']
                        elif metric_name == 'Actions → Tir/90':
                            distribution = df_comparison['Actions menant à un tir par 90 minutes']
                        elif metric_name == 'Passes dernier tiers/90':
                            distribution = df_comparison['Passes dans le dernier tiers'] / (df_comparison['Minutes jouées'] / 90)
                        else:
                            base_column = metric_name.replace('/90', '').replace('Passes D.', 'Passes décisives').replace('Passes prog.', 'Passes progressives')
                            distribution = df_comparison[base_column] / (df_comparison['Minutes jouées'] / 90)
                        
                        avg_percentile = (distribution < avg_val).mean() * 100
                        avg_percentiles.append(avg_percentile)
                    else:
                        avg_percentiles.append(50)
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=avg_percentiles,
                    theta=list(offensive_metrics.keys()),
                    mode='lines',
                    line=dict(color='rgba(255,255,255,0.8)', width=3, dash='dash'),
                    name=f'Moyenne {selected_competition}',
                    showlegend=True,
                    hovertemplate='<b>%{theta}</b><br>Moyenne ligue: %{customdata:.2f}<extra></extra>',
                    customdata=avg_values
                ))
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100],
                            gridcolor='rgba(255,255,255,0.3)',
                            tickcolor=COLORS['light'],
                            tickfont=dict(color=COLORS['light'], size=11, family='Inter'),
                            showticklabels=True,
                            tickmode='linear',
                            tick0=0,
                            dtick=20
                        ),
                        angularaxis=dict(
                            gridcolor='rgba(255,255,255,0.3)',
                            tickcolor=COLORS['light'],
                            tickfont=dict(color=COLORS['light'], size=12, family='Inter', weight='bold'),
                            linecolor='rgba(255,255,255,0.5)'
                        ),
                        bgcolor='rgba(26, 26, 26, 0.9)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=COLORS['light'], family='Inter'),
                    title=dict(
                        text="📊 Radar Offensif Professionnel (Percentiles)",
                        font=dict(size=18, color=COLORS['light'], family='Inter', weight='bold'),
                        x=0.5,
                        y=0.95
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="center",
                        x=0.5,
                        font=dict(color=COLORS['light'], size=11, family='Inter'),
                        bgcolor='rgba(26, 26, 26, 0.8)',
                        bordercolor=COLORS['light'],
                        borderwidth=1
                    ),
                    height=480,
                    annotations=[
                        dict(
                            text=f"🏆 Performance vs Moyenne {selected_competition}",
                            showarrow=False,
                            x=0.5,
                            y=-0.15,
                            xref="paper",
                            yref="paper",
                            font=dict(color=COLORS['light'], size=13, family='Inter'),
                            bgcolor=COLORS['primary'],
                            bordercolor=COLORS['light'],
                            borderwidth=2,
                            borderradius=5
                        )
                    ]
                )
                
                st.plotly_chart(fig_radar, use_container_width=True)
            
            with col2:
                # Pourcentages de réussite offensifs
                pourcentages_off = {
                    'Conversion (Buts/Tirs)': (player_data['Buts'] / player_data['Tirs'] * 100) if player_data['Tirs'] > 0 else 0,
                    'Précision tirs': player_data.get('Pourcentage de tirs cadrés', 0),
                    'Efficacité passes clés': (player_data['Passes décisives'] / player_data['Passes clés'] * 100) if player_data['Passes clés'] > 0 else 0
                }
                
                pourcentages_off = {k: v if pd.notna(v) else 0 for k, v in pourcentages_off.items()}
                
                fig_gauge_off = make_subplots(
                    rows=1, cols=3,
                    specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
                    subplot_titles=list(pourcentages_off.keys())
                )
                
                colors_off = [COLORS['primary'], COLORS['secondary'], COLORS['success']]
                for i, (metric, value) in enumerate(pourcentages_off.items()):
                    fig_gauge_off.add_trace(
                        go.Indicator(
                            mode="gauge+number",
                            value=value,
                            gauge=dict(
                                axis=dict(range=[0, 100]),
                                bar=dict(color=colors_off[i], thickness=0.3),
                                bgcolor="rgba(26, 26, 26, 0.8)",
                                borderwidth=3,
                                bordercolor=COLORS['light'],
                                steps=[
                                    {'range': [0, 50], 'color': 'rgba(255,255,255,0.1)'},
                                    {'range': [50, 80], 'color': 'rgba(255,255,255,0.2)'},
                                    {'range': [80, 100], 'color': 'rgba(255,255,255,0.3)'}
                                ]
                            ),
                            number={'suffix': '%', 'font': {'color': COLORS['light'], 'family': 'Inter', 'size': 16}}
                        ),
                        row=1, col=i+1
                    )
                
                fig_gauge_off.update_layout(
                    height=320, 
                    title_text="⚽ Pourcentages de Réussite Offensive",
                    title_font=dict(color=COLORS['light'], size=16, family='Inter'),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=COLORS['light'], family='Inter')
                )
                st.plotly_chart(fig_gauge_off, use_container_width=True)
                
                # Graphique de comparaison offensive
                offensive_comparison = {
                    'Buts/90': player_data['Buts par 90 minutes'],
                    'Passes D./90': player_data['Passes décisives par 90 minutes'],
                    'xG/90': player_data['Buts attendus par 90 minutes']
                }
                
                avg_comparison_off = {
                    'Buts/90': df_comparison['Buts par 90 minutes'].mean(),
                    'Passes D./90': df_comparison['Passes décisives par 90 minutes'].mean(),
                    'xG/90': df_comparison['Buts attendus par 90 minutes'].mean()
                }
                
                fig_off_comp = go.Figure()
                
                fig_off_comp.add_trace(go.Bar(
                    name=selected_player,
                    x=list(offensive_comparison.keys()),
                    y=list(offensive_comparison.values()),
                    marker_color=COLORS['primary'],
                    marker_line=dict(color=COLORS['light'], width=2)
                ))
                
                fig_off_comp.add_trace(go.Bar(
                    name='Moyenne compétition',
                    x=list(avg_comparison_off.keys()),
                    y=list(avg_comparison_off.values()),
                    marker_color=COLORS['secondary'],
                    marker_line=dict(color=COLORS['light'], width=2)
                ))
                
                fig_off_comp.update_layout(
                    title=dict(
                        text='📈 Actions Offensives par 90min vs Moyenne',
                        font=dict(color=COLORS['light'], size=16, family='Inter'),
                        x=0.5
                    ),
                    barmode='group',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=COLORS['light'], family='Inter'),
                    xaxis=dict(tickfont=dict(color=COLORS['light'], family='Inter')),
                    yaxis=dict(tickfont=dict(color=COLORS['light'], family='Inter'), gridcolor='rgba(255,255,255,0.2)'),
                    legend=dict(font=dict(color=COLORS['light'], family='Inter')),
                    height=420
                )
                
                st.plotly_chart(fig_off_comp, use_container_width=True)
            
            # Scatter plot pour comparaison offensive
            st.markdown("<div class='subsection-title'>🔍 Analyse Comparative Offensive</div>", unsafe_allow_html=True)
            
            col_scatter1, col_scatter2 = st.columns(2)
            
            with col_scatter1:
                metric_options_off = [
                    'Buts', 'Passes décisives', 'Tirs', 'Buts attendus (xG)',
                    'Passes décisives attendues (xAG)', 'Passes clés', 'Actions menant à un tir',
                    'Pourcentage de tirs cadrés'
                ]
                
                x_metric_off = st.selectbox("Métrique X", metric_options_off, index=0, key="x_off")
                y_metric_off = st.selectbox("Métrique Y", metric_options_off, index=1, key="y_off")
            
            with col_scatter2:
                fig_scatter_off = go.Figure()
                
                if x_metric_off not in ['Pourcentage de tirs cadrés']:
                    x_data = df_comparison[x_metric_off] / (df_comparison['Minutes jouées'] / 90)
                    x_player = player_data[x_metric_off] / (player_data['Minutes jouées'] / 90)
                    x_title = f"{x_metric_off} par 90min"
                else:
                    x_data = df_comparison[x_metric_off]
                    x_player = player_data[x_metric_off]
                    x_title = x_metric_off
                    
                if y_metric_off not in ['Pourcentage de tirs cadrés']:
                    y_data = df_comparison[y_metric_off] / (df_comparison['Minutes jouées'] / 90)
                    y_player = player_data[y_metric_off] / (player_data['Minutes jouées'] / 90)
                    y_title = f"{y_metric_off} par 90min"
                else:
                    y_data = df_comparison[y_metric_off]
                    y_player = player_data[y_metric_off]
                    y_title = y_metric_off
                
                fig_scatter_off.add_trace(go.Scatter(
                    x=x_data,
                    y=y_data,
                    mode='markers',
                    name='Autres joueurs',
                    marker=dict(color=COLORS['accent'], size=8, opacity=0.7, line=dict(color=COLORS['light'], width=1)),
                    text=df_comparison['Joueur'],
                    hovertemplate='<b>%{text}</b><br>' + x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
                ))
                
                fig_scatter_off.add_trace(go.Scatter(
                    x=[x_player],
                    y=[y_player],
                    mode='markers',
                    name=selected_player,
                    marker=dict(color=COLORS['primary'], size=25, symbol='star', line=dict(color=COLORS['light'], width=3)),
                    hovertemplate=f'<b>{selected_player}</b><br>' + x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
                ))
                
                fig_scatter_off.update_layout(
                    title=dict(text=f"📊 {x_title} vs {y_title}", font=dict(size=15, color=COLORS['light'], family='Inter'), x=0.5),
                    xaxis=dict(title=dict(text=x_title, font=dict(color=COLORS['light'], family='Inter')), tickfont=dict(color=COLORS['light'], family='Inter')),
                    yaxis=dict(title=dict(text=y_title, font=dict(color=COLORS['light'], family='Inter')), tickfont=dict(color=COLORS['light'], family='Inter')),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=COLORS['light'], family='Inter'),
                    legend=dict(font=dict(color=COLORS['light'], family='Inter')),
                    height=420
                )
                
                st.plotly_chart(fig_scatter_off, use_container_width=True)
            
            # Métriques offensives par 90 minutes
            st.markdown("<div class='subsection-title'>📊 Statistiques offensives par 90 minutes</div>", unsafe_allow_html=True)
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Buts/90min", f"{player_data['Buts par 90 minutes']:.2f}")
            with col2:
                st.metric("Passes D./90min", f"{player_data['Passes décisives par 90 minutes']:.2f}")
            with col3:
                st.metric("xG/90min", f"{player_data['Buts attendus par 90 minutes']:.2f}")
            with col4:
                st.metric("Actions → Tir/90min", f"{player_data['Actions menant à un tir par 90 minutes']:.2f}")
            with col5:
                efficiency_off = (player_data['Buts'] + player_data['Passes décisives']) / player_data.get('Tirs', 1) * 100 if player_data.get('Tirs', 0) > 0 else 0
                st.metric("Efficacité Offensive", f"{efficiency_off:.1f}%")
    
        with tab2:
            st.markdown("<div class='section-title'>🛡️ Performance Défensive</div>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Graphique des actions défensives
                actions_def = {
                    'Tacles gagnants': player_data['Tacles gagnants'],
                    'Interceptions': player_data['Interceptions'],
                    'Ballons récupérés': player_data['Ballons récupérés'],
                    'Duels aériens gagnés': player_data['Duels aériens gagnés'],
                    'Dégagements': player_data['Dégagements']
                }
                
                fig_bar = go.Figure(data=[go.Bar(
                    x=list(actions_def.keys()),
                    y=list(actions_def.values()),
                    marker=dict(
                        color=COLORS['gradient'],
                        line=dict(color=COLORS['light'], width=2)
                    ),
                    text=list(actions_def.values()),
                    textposition='outside',
                    textfont=dict(color=COLORS['light'], size=12, family='Inter')
                )])
                
                fig_bar.update_layout(
                    title=dict(
                        text="🛡️ Actions Défensives",
                        font=dict(size=18, color=COLORS['light'], family='Inter', weight='bold'),
                        x=0.5
                    ),
                    xaxis=dict(
                        tickfont=dict(color=COLORS['light'], family='Inter'),
                        tickangle=45
                    ),
                    yaxis=dict(
                        tickfont=dict(color=COLORS['light'], family='Inter'),
                        gridcolor='rgba(255,255,255,0.2)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=COLORS['light'], family='Inter'),
                    height=400
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                
                # Radar défensif professionnel
                st.markdown("<div class='subsection-title'>🛡️ Radar Défensif Professionnel</div>", unsafe_allow_html=True)
                
                defensive_metrics = {
                    'Tacles/90': player_data['Tacles gagnants'] / (player_data['Minutes jouées'] / 90),
                    'Interceptions/90': player_data['Interceptions'] / (player_data['Minutes jouées'] / 90),
                    'Ballons récupérés/90': player_data['Ballons récupérés'] / (player_data['Minutes jouées'] / 90),
                    'Duels défensifs/90': player_data.get('Duels défensifs gagnés', 0) / (player_data['Minutes jouées'] / 90),
                    'Duels aériens/90': player_data['Duels aériens gagnés'] / (player_data['Minutes jouées'] / 90),
                    'Dégagements/90': player_data['Dégagements'] / (player_data['Minutes jouées'] / 90),
                    'Tirs bloqués/90': player_data.get('Tirs bloqués', 0) / (player_data['Minutes jouées'] / 90),
                    '% Duels gagnés': player_data.get('Pourcentage de duels gagnés', 0),
                    '% Duels aériens': player_data['Pourcentage de duels aériens gagnés'],
                    'Total Blocs/90': player_data.get('Total de blocs (tirs et passes)', 0) / (player_data['Minutes jouées'] / 90)
                }
                
                # Calculer les percentiles défensifs
                def_percentile_values = []
                def_avg_values = []
                for metric, value in defensive_metrics.items():
                    try:
                        if metric == 'Tacles/90':
                            distribution = df_comparison['Tacles gagnants'] / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Interceptions/90':
                            distribution = df_comparison['Interceptions'] / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Ballons récupérés/90':
                            distribution = df_comparison['Ballons récupérés'] / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Duels défensifs/90':
                            distribution = df_comparison.get('Duels défensifs gagnés', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Duels aériens/90':
                            distribution = df_comparison['Duels aériens gagnés'] / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Dégagements/90':
                            distribution = df_comparison['Dégagements'] / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Tirs bloqués/90':
                            distribution = df_comparison.get('Tirs bloqués', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                        elif metric == '% Duels gagnés':
                            distribution = df_comparison.get('Pourcentage de duels gagnés', pd.Series([0]*len(df_comparison)))
                        elif metric == '% Duels aériens':
                            distribution = df_comparison['Pourcentage de duels aériens gagnés']
                        elif metric == 'Total Blocs/90':
                            distribution = df_comparison.get('Total de blocs (tirs et passes)', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                        
                        distribution = distribution.replace([np.inf, -np.inf], np.nan).dropna()
                        value = value if not np.isnan(value) and not np.isinf(value) else 0
                        
                        if len(distribution) > 0:
                            percentile = (distribution < value).mean() * 100
                            avg_comp = distribution.mean()
                        else:
                            percentile = 50
                            avg_comp = 0
                        
                        def_percentile_values.append(min(percentile, 100))
                        def_avg_values.append(avg_comp)
                    except:
                        def_percentile_values.append(50)
                        def_avg_values.append(0)
                
                # Radar défensif
                fig_def_radar = go.Figure()
                
                fig_def_radar.add_trace(go.Scatterpolar(
                    r=def_percentile_values,
                    theta=list(defensive_metrics.keys()),
                    fill='toself',
                    fillcolor=f'rgba({0}, {107}, {60}, 0.3)',
                    line=dict(color=COLORS['secondary'], width=4),
                    marker=dict(color=COLORS['secondary'], size=10, symbol='circle'),
                    name=f'{selected_player}',
                    hovertemplate='<b>%{theta}</b><br>Percentile: %{r:.0f}<br>Valeur: %{customdata:.2f}<extra></extra>',
                    customdata=list(defensive_metrics.values())
                ))
                
                # Ligne moyenne défensive
                def_avg_percentiles = []
                for i, avg_val in enumerate(def_avg_values):
                    try:
                        if avg_val > 0:
                            metric_name = list(defensive_metrics.keys())[i]
                            if metric_name == 'Tacles/90':
                                distribution = df_comparison['Tacles gagnants'] / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == 'Interceptions/90':
                                distribution = df_comparison['Interceptions'] / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == 'Ballons récupérés/90':
                                distribution = df_comparison['Ballons récupérés'] / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == 'Duels défensifs/90':
                                distribution = df_comparison.get('Duels défensifs gagnés', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == 'Duels aériens/90':
                                distribution = df_comparison['Duels aériens gagnés'] / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == 'Dégagements/90':
                                distribution = df_comparison['Dégagements'] / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == 'Tirs bloqués/90':
                                distribution = df_comparison.get('Tirs bloqués', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == '% Duels gagnés':
                                distribution = df_comparison.get('Pourcentage de duels gagnés', pd.Series([0]*len(df_comparison)))
                            elif metric_name == '% Duels aériens':
                                distribution = df_comparison['Pourcentage de duels aériens gagnés']
                            elif metric_name == 'Total Blocs/90':
                                distribution = df_comparison.get('Total de blocs (tirs et passes)', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                            
                            distribution = distribution.replace([np.inf, -np.inf], np.nan).dropna()
                            if len(distribution) > 0:
                                avg_percentile = (distribution < avg_val).mean() * 100
                                def_avg_percentiles.append(avg_percentile)
                            else:
                                def_avg_percentiles.append(50)
                        else:
                            def_avg_percentiles.append(50)
                    except:
                        def_avg_percentiles.append(50)
                
                fig_def_radar.add_trace(go.Scatterpolar(
                    r=def_avg_percentiles,
                    theta=list(defensive_metrics.keys()),
                    mode='lines',
                    line=dict(color='rgba(255,255,255,0.8)', width=3, dash='dash'),
                    name=f'Moyenne {selected_competition}',
                    showlegend=True,
                    hovertemplate='<b>%{theta}</b><br>Moyenne ligue: %{customdata:.2f}<extra></extra>',
                    customdata=def_avg_values
                ))
                
                fig_def_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100],
                            gridcolor='rgba(255,255,255,0.3)',
                            tickcolor=COLORS['light'],
                            tickfont=dict(color=COLORS['light'], size=11, family='Inter'),
                            showticklabels=True,
                            tickmode='linear',
                            tick0=0,
                            dtick=20
                        ),
                        angularaxis=dict(
                            gridcolor='rgba(255,255,255,0.3)',
                            tickcolor=COLORS['light'],
                            tickfont=dict(color=COLORS['light'], size=12, family='Inter', weight='bold'),
                            linecolor='rgba(255,255,255,0.5)'
                        ),
                        bgcolor='rgba(26, 26, 26, 0.9)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=COLORS['light'], family='Inter'),
                    title=dict(
                        text="🛡️ Radar Défensif Professionnel (Percentiles)",
                        font=dict(size=18, color=COLORS['light'], family='Inter', weight='bold'),
                        x=0.5,
                        y=0.95
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="center",
                        x=0.5,
                        font=dict(color=COLORS['light'], size=11, family='Inter'),
                        bgcolor='rgba(26, 26, 26, 0.8)',
                        bordercolor=COLORS['light'],
                        borderwidth=1
                    ),
                    height=480,
                    annotations=[
                        dict(
                            text=f"🏆 Performance Défensive vs Moyenne {selected_competition}",
                            showarrow=False,
                            x=0.5,
                            y=-0.15,
                            xref="paper",
                            yref="paper",
                            font=dict(color=COLORS['light'], size=13, family='Inter'),
                            bgcolor=COLORS['secondary'],
                            bordercolor=COLORS['light'],
                            borderwidth=2,
                            borderradius=5
                        )
                    ]
                )
                
                st.plotly_chart(fig_def_radar, use_container_width=True)
